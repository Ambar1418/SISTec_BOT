"""
scraper.py - College Website Scraper
Scrapes text data from SISTEC website using BeautifulSoup and Requests.
Handles crawling, cleaning, deduplication, and caching.
"""

import os
import re
import json
import time
import hashlib
import logging
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Dict, Set, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
BASE_URL = "https://www.sistec.ac.in/"
DATA_DIR = "data"
SCRAPED_FILE = os.path.join(DATA_DIR, "scraped_data.json")
RAW_TEXT_FILE = os.path.join(DATA_DIR, "raw_text.txt")

# Priority pages to scrape
PRIORITY_PAGES = [
    "https://www.sistec.ac.in/",
    "https://www.sistec.ac.in/about-us",
    "https://www.sistec.ac.in/admissions",
    "https://www.sistec.ac.in/courses",
    "https://www.sistec.ac.in/placements",
    "https://www.sistec.ac.in/facilities",
    "https://www.sistec.ac.in/departments",
    "https://www.sistec.ac.in/contact-us",
    "https://www.sistec.ac.in/events",
    "https://www.sistec.ac.in/notice-board",
    "https://www.sistec.ac.in/faculty",
    "https://www.sistec.ac.in/campus-life",
    "https://www.sistec.ac.in/research",
    "https://www.sistec.ac.in/gallery",
    "https://www.sistec.ac.in/naac",
    "https://www.sistec.ac.in/iqac",
]

# Tags to extract meaningful text from
CONTENT_TAGS = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "span", "div"]

# Tags to skip entirely
SKIP_TAGS = ["script", "style", "nav", "footer", "header", "noscript", "iframe", "form"]

MAX_PAGES = 3           # Maximum pages to crawl (limited to 3 for Gemini free tier quota)
REQUEST_DELAY = 0.8     # Seconds between requests (be polite)
REQUEST_TIMEOUT = 15    # Seconds before giving up
MAX_RETRIES = 3         # Retry attempts for failed requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────

def is_same_domain(url: str, base: str) -> bool:
    """Check if a URL belongs to the same domain as the base URL."""
    return urlparse(url).netloc == urlparse(base).netloc


def normalize_url(url: str) -> str:
    """Remove fragments and trailing slashes for deduplication."""
    parsed = urlparse(url)
    normalized = parsed._replace(fragment="").geturl()
    return normalized.rstrip("/")


def is_valid_url(url: str) -> bool:
    """Filter out unwanted file types and external links."""
    skip_extensions = [".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip",
                       ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
                       ".mp4", ".mp3", ".avi", ".svg", ".ico", ".css", ".js"]
    parsed = urlparse(url)
    path_lower = parsed.path.lower()
    if any(path_lower.endswith(ext) for ext in skip_extensions):
        return False
    return bool(parsed.scheme in ["http", "https"] and parsed.netloc)


def clean_text(text: str) -> str:
    """Clean and normalize scraped text."""
    # Remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E\u00A0-\uFFFF]', '', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def compute_hash(text: str) -> str:
    """Generate MD5 hash for deduplication."""
    return hashlib.md5(text.encode()).hexdigest()


# ─────────────────────────────────────────────
# Core Fetcher
# ─────────────────────────────────────────────

def fetch_page(url: str, session: requests.Session) -> Optional[BeautifulSoup]:
    """
    Fetch a URL with retry logic and return a BeautifulSoup object.
    Returns None on failure.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            # Only parse HTML content
            if "text/html" not in response.headers.get("Content-Type", ""):
                return None
            soup = BeautifulSoup(response.text, "html.parser")
            return soup
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error on {url}: {e} (attempt {attempt})")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error on {url}: {e} (attempt {attempt})")
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on {url} (attempt {attempt})")
        except Exception as e:
            logger.error(f"Unexpected error on {url}: {e}")
            break
        if attempt < MAX_RETRIES:
            time.sleep(REQUEST_DELAY * attempt)  # Exponential backoff
    return None


# ─────────────────────────────────────────────
# Text Extractor
# ─────────────────────────────────────────────

def extract_text_from_soup(soup: BeautifulSoup, url: str) -> Dict:
    """
    Extract meaningful text from parsed HTML.
    Skips navigation, scripts, styles, and other junk.
    Returns a dict with url, title, and content.
    """
    # Remove unwanted tags completely
    for tag in soup.find_all(SKIP_TAGS):
        tag.decompose()

    # Also remove common navigation/footer class names
    for selector in ["nav", ".navbar", ".footer", ".header", ".menu",
                     "#nav", "#footer", "#header", "#menu", ".breadcrumb",
                     ".pagination", ".sidebar", ".widget", ".advertisement"]:
        for element in soup.select(selector):
            element.decompose()

    # Get page title
    title = ""
    if soup.title:
        title = clean_text(soup.title.get_text())

    # Extract main content - fallback to body if main/article not found
    content_area = soup.find("main") or soup.find("article") or soup.find("body") or soup

    # Get all text from the content area, separated by newlines
    full_content = clean_text(content_area.get_text(separator="\n", strip=True))
    
    # Simple deduplication of consecutive identical lines
    lines = []
    for line in full_content.split('\n'):
        line = line.strip()
        if line and len(line) > 20 and (not lines or line != lines[-1]):
            lines.append(line)
            
    full_content = "\n".join(lines)

    return {
        "url": url,
        "title": title,
        "content": full_content,
    }


# ─────────────────────────────────────────────
# Link Extractor
# ─────────────────────────────────────────────

def extract_links(soup: BeautifulSoup, current_url: str) -> List[str]:
    """Extract all valid internal links from a page."""
    links = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        # Build absolute URL
        absolute_url = urljoin(current_url, href)
        normalized = normalize_url(absolute_url)
        if is_valid_url(normalized) and is_same_domain(normalized, BASE_URL):
            links.append(normalized)
    return list(set(links))


# ─────────────────────────────────────────────
# Main Scraper
# ─────────────────────────────────────────────

def scrape_website(progress_callback=None) -> List[Dict]:
    """
    Main scraping function. Crawls the SISTEC website and collects text data.
    
    Args:
        progress_callback: Optional callable(current, total, message) for UI progress bars.
    
    Returns:
        List of dicts with {url, title, content}
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    # Check if scraping already done
    if os.path.exists(SCRAPED_FILE):
        logger.info("Found cached scraped data. Loading from file...")
        with open(SCRAPED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} pages from cache.")
        return data

    logger.info("Starting fresh scrape of SISTEC website...")

    visited: Set[str] = set()
    to_visit: List[str] = [normalize_url(url) for url in PRIORITY_PAGES]
    results: List[Dict] = []
    seen_content_hashes: Set[str] = set()

    session = requests.Session()
    session.headers.update(HEADERS)

    total_estimated = min(MAX_PAGES, len(to_visit) + 20)
    current = 0

    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.pop(0)

        if url in visited:
            continue
        visited.add(url)
        current += 1

        if progress_callback:
            progress_callback(current, total_estimated, f"Scraping: {url[:60]}...")

        logger.info(f"[{current}/{total_estimated}] Scraping: {url}")

        soup = fetch_page(url, session)
        if soup is None:
            logger.warning(f"Skipping {url} — could not fetch.")
            continue

        # Extract text data
        page_data = extract_text_from_soup(soup, url)
        content = page_data["content"]

        if len(content) < 50:
            logger.info(f"Skipping {url} — insufficient content.")
            continue

        # Deduplicate by content hash — use FULL content hash, not just first 500 chars.
        # The SISTEC site has the same header/nav on every page, so hashing 500 chars
        # would falsely mark all pages as duplicates.
        content_hash = compute_hash(content)  # Hash entire content
        if content_hash in seen_content_hashes:
            logger.info(f"Skipping {url} — exact duplicate content.")
            continue
        seen_content_hashes.add(content_hash)

        results.append(page_data)

        # Discover new internal links
        new_links = extract_links(soup, url)
        for link in new_links:
            if link not in visited and link not in to_visit:
                to_visit.append(link)

        time.sleep(REQUEST_DELAY)  # Be polite to the server

    logger.info(f"Scraping complete. Collected {len(results)} unique pages.")

    # Save results to cache
    with open(SCRAPED_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Also save as plain text for easy inspection
    with open(RAW_TEXT_FILE, "w", encoding="utf-8") as f:
        for page in results:
            f.write(f"\n{'='*60}\n")
            f.write(f"URL: {page['url']}\n")
            f.write(f"TITLE: {page['title']}\n")
            f.write(f"{'='*60}\n")
            f.write(page['content'])
            f.write("\n")

    logger.info(f"Data saved to {SCRAPED_FILE} and {RAW_TEXT_FILE}")
    return results


# ─────────────────────────────────────────────
# Clear Cache Utility
# ─────────────────────────────────────────────

def clear_scrape_cache():
    """Delete cached scrape data to force a fresh scrape."""
    for path in [SCRAPED_FILE, RAW_TEXT_FILE]:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Deleted cache: {path}")


if __name__ == "__main__":
    # Run standalone for testing
    data = scrape_website()
    print(f"\nScraped {len(data)} pages.")
    if data:
        print(f"First page: {data[0]['url']}")
        print(f"Content preview: {data[0]['content'][:300]}...")
