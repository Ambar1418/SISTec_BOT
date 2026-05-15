"""
utils/helpers.py - Utility functions for the SISTec chatbot
"""

import os
import re
import logging
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)


def format_sources(sources: List[str]) -> str:
    """Format source URLs into readable markdown."""
    if not sources:
        return ""
    formatted = "\n\n---\n**Sources:**\n"
    for url in sources[:5]:
        path = url.rstrip("/").split("/")[-1].replace("-", " ").replace("_", " ").title()
        label = path if path else "Home"
        formatted += f"- [{label}]({url})\n"
    return formatted


def get_timestamp() -> str:
    """Return current time as HH:MM string."""
    return datetime.now().strftime("%H:%M")


def sanitize_input(text: str) -> str:
    """Sanitize user input — strip excessive whitespace and limit length."""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text[:500]


def check_env_keys() -> dict:
    """Check which API keys are configured."""
    from dotenv import load_dotenv
    load_dotenv()
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY", "").strip()),
        "gemini": bool(os.getenv("GEMINI_API_KEY", "").strip()),
    }


def scrape_cache_exists() -> bool:
    """Check if scrape cache file exists."""
    return os.path.exists(os.path.join("data", "scraped_data.json"))


def vectorstore_cache_exists() -> bool:
    """Check if vector store index exists."""
    return os.path.exists(os.path.join("vectorstore", "index.faiss"))


def get_data_stats() -> dict:
    """Return statistics about current data state."""
    stats = {
        "scrape_cache": scrape_cache_exists(),
        "vectorstore_cache": vectorstore_cache_exists(),
        "data_file_size_kb": 0,
    }
    data_path = os.path.join("data", "scraped_data.json")
    if os.path.exists(data_path):
        stats["data_file_size_kb"] = os.path.getsize(data_path) // 1024
    return stats


def estimate_tokens(text: str) -> int:
    """Rough estimate of token count (1 token ≈ 4 chars)."""
    return len(text) // 4
