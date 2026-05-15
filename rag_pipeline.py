"""
rag_pipeline.py - RAG (Retrieval-Augmented Generation) Pipeline
Compatible with LangChain 1.x (LCEL-based — no deprecated RetrievalQA)
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

# LangChain imports (LangChain 1.x LCEL style)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

load_dotenv()

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
VECTORSTORE_DIR = "vectorstore"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K_RESULTS = 5

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

SYSTEM_PROMPT = """You are SISTec Assistant, an intelligent AI chatbot for SISTec \
(Sagar Institute of Science, Technology & Engineering) college.

Answer questions about the college using ONLY the provided context from the official website.

Rules:
- Answer about courses, admissions, placements, faculty, departments, facilities, \
events, and campus life.
- Be helpful, concise, and professional.
- If the context does not contain enough information, say exactly:
  "I could not find this information on the college website. \
Please visit https://www.sistec.ac.in/ or contact the college directly."
- Do NOT make up or hallucinate information.
- Format lists and structured data clearly.

Context:
{context}

Question: {question}

Answer:"""


# ─────────────────────────────────────────────
# Text Chunking
# ─────────────────────────────────────────────

def chunk_documents(pages: List[Dict]) -> List[Document]:
    """Split scraped pages into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    documents = []
    seen_chunk_hashes = set()
    import hashlib
    
    for page in pages:
        content = page.get("content", "").strip()
        if not content:
            continue

        prefixed = (
            f"Page: {page.get('title', 'Unknown')}\n"
            f"URL: {page.get('url', '')}\n\n"
            f"{content}"
        )

        chunks = splitter.split_text(prefixed)
        for i, chunk in enumerate(chunks):
            # Hash just the content (ignore URL prefix) to deduplicate shared headers/footers
            chunk_hash = hashlib.md5(chunk.split("\n\n", 1)[-1].encode()).hexdigest()
            if chunk_hash not in seen_chunk_hashes:
                seen_chunk_hashes.add(chunk_hash)
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "source": page.get("url", ""),
                        "title": page.get("title", ""),
                        "chunk_index": i,
                    },
                ))

    logger.info(f"Created {len(documents)} unique chunks from {len(pages)} pages.")
    return documents


# ─────────────────────────────────────────────
# Embeddings
# ─────────────────────────────────────────────

def load_embeddings():
    """Dummy embeddings loader."""
    logger.info("Embeddings temporarily disabled.")
    return None


# ─────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────

def load_llm():
    """Load the LLM based on LLM_PROVIDER."""
    if LLM_PROVIDER == "groq" and GROQ_API_KEY:
        try:
            from langchain_groq import ChatGroq
            logger.info("Using Groq LLM (llama-3.3-70b-versatile).")
            return ChatGroq(
                model_name="llama-3.3-70b-versatile",
                groq_api_key=GROQ_API_KEY,
                temperature=0.2,
            )
        except ImportError:
            logger.warning("langchain_groq not installed. Falling back to Gemini.")

    if LLM_PROVIDER == "gemini" and GEMINI_API_KEY:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            logger.info("Using Google Gemini LLM (gemini-2.5-flash).")
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=GEMINI_API_KEY,
                temperature=0.2,
            )
        except ImportError:
            logger.warning("langchain_google_genai not installed. Falling back to OpenAI.")

    if OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        logger.info("Using OpenAI GPT-4o-mini LLM.")
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
            temperature=0.2,
            max_tokens=1024,
        )

    raise ValueError(
        "No valid API key found! Set OPENAI_API_KEY or GEMINI_API_KEY in your .env file."
    )


# ─────────────────────────────────────────────
# Vector Store
# ─────────────────────────────────────────────

def build_vectorstore(documents: List[Document]) -> FAISS:
    """Build and persist a FAISS vector store."""
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    embeddings = load_embeddings()
    logger.info(f"Building FAISS index with {len(documents)} chunks...")
    vs = FAISS.from_documents(documents, embeddings)
    vs.save_local(VECTORSTORE_DIR)
    logger.info(f"Vector store saved to '{VECTORSTORE_DIR}'.")
    return vs


def load_vectorstore() -> Optional[FAISS]:
    """Load an existing FAISS vector store from disk."""
    if not os.path.exists(os.path.join(VECTORSTORE_DIR, "index.faiss")):
        return None
    embeddings = load_embeddings()
    logger.info("Loading cached FAISS vector store...")
    return FAISS.load_local(
        VECTORSTORE_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )


def vectorstore_exists() -> bool:
    """Check if a FAISS index file exists on disk."""
    return os.path.exists(os.path.join(VECTORSTORE_DIR, "index.faiss"))


def clear_vectorstore():
    """Delete the saved vector store to force a rebuild."""
    import shutil
    if os.path.exists(VECTORSTORE_DIR):
        shutil.rmtree(VECTORSTORE_DIR)
        logger.info("Vector store deleted.")


# ─────────────────────────────────────────────
# LCEL RAG Chain (LangChain 1.x)
# ─────────────────────────────────────────────

class RAGChain:
    """
    Wrapper around an LCEL-based RAG pipeline.
    Replaces the deprecated RetrievalQA for LangChain 1.x compatibility.
    """

    def __init__(self, vectorstore: FAISS):
        self.llm = load_llm()
        self.prompt = PromptTemplate(
            template=SYSTEM_PROMPT,
            input_variables=["context", "question"],
        )
        self.retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": TOP_K_RESULTS,
                "fetch_k": TOP_K_RESULTS * 3,
                "lambda_mult": 0.7,
            },
        )

        # Build the LCEL chain
        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join(d.page_content for d in docs)

        self._chain = (
            {
                "context": self.retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def invoke(self, question: str) -> Tuple[str, List[str]]:
        """
        Run the RAG chain for a question.
        Returns (answer_text, list_of_source_urls).
        """
        try:
            # Get answer
            answer = self._chain.invoke(question)

            # Fetch source docs separately for citation
            source_docs = self.retriever.invoke(question)
            sources = list({
                doc.metadata.get("source", "")
                for doc in source_docs
                if doc.metadata.get("source")
            })

            return answer.strip(), sources

        except Exception as e:
            error_msg = str(e)
            logger.error(f"RAG chain error: {error_msg}")
            
            if "429" in error_msg or "Quota exceeded" in error_msg:
                user_msg = "⚠️ API Rate Limit Exceeded: You are using the free tier of the Gemini API which limits how fast you can ask questions. Please wait about 60 seconds and try again."
            else:
                user_msg = "I encountered an error while processing your question. Please try again."
                
            return (user_msg, [])


# ─────────────────────────────────────────────
# Public API used by app.py
# ─────────────────────────────────────────────

def initialize_rag(pages: List[Dict], progress_callback=None) -> "RAGChain":
    """
    Full initialization: chunk → build/load vector store → build chain.
    Returns a RAGChain instance ready to answer questions.
    """
    if vectorstore_exists():
        logger.info("Using cached vector store.")
        if progress_callback:
            progress_callback("Loading existing vector index...")
        vs = load_vectorstore()
    else:
        if progress_callback:
            progress_callback("Chunking documents...")
        documents = chunk_documents(pages)

        if progress_callback:
            progress_callback(f"Building vector index from {len(documents)} chunks...")
        vs = build_vectorstore(documents)

    if progress_callback:
        progress_callback("Building RAG chain...")

    return RAGChain(vs)


def query_rag(chain: "RAGChain", question: str) -> Tuple[str, List[str]]:
    """Thin wrapper so app.py doesn't need to change."""
    return chain.invoke(question)


if __name__ == "__main__":
    # Test loading the vectorstore if it exists
    if vectorstore_exists():
        chain = initialize_rag([])
        answer, sources = query_rag(chain, "What courses does SISTec offer?")
        print("Answer:", answer)
        print("Sources:", sources)
    else:
        print("Vectorstore not found. Run scraper and builder locally first.")