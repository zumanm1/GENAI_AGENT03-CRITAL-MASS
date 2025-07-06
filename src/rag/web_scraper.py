"""Web Scraper Connector

Part of Feature 0900 – Enhanced RAG with More Data Sources.

Given a public URL, this module fetches the page, extracts human-readable
text, and ingests it into the ChromaDB vector store so it can be used as
context during chat interactions.
"""
from __future__ import annotations

import logging
import uuid
from typing import Tuple

import requests
from bs4 import BeautifulSoup

from src.core.chromadb_service import chromadb_service

logger = logging.getLogger(__name__)


def _extract_text(html: str) -> str:
    """Return visible text from HTML, stripped of scripts/styles."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    lines = [line.strip() for line in soup.get_text(
        separator="\n").splitlines()]
    return "\n".join([line for line in lines if line])


def scrape_and_ingest(url: str) -> Tuple[bool, str]:
    """Fetch *url*, extract text, and add to vector DB.
    Returns (success, msg)."""
    try:
        logger.info(f"Scraping URL: {url}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        text = _extract_text(resp.text)
        if len(text) < 200:
            return False, "Page contained insufficient text to be useful."

        doc_id = str(uuid.uuid4())
        metadata = {"source": "web", "url": url}

        added = chromadb_service.add_document(doc_id, text, metadata)
        if not added:
            return False, "Failed to add document to vector database."

        logger.info(
            f"Ingested {len(text)} characters from {url} (id={doc_id})")
        return True, f"Ingested {len(text)} chars from {url}"

    except requests.RequestException as e:
        logger.error(f"HTTP error scraping {url}: {e}")
        return False, str(e)
    except Exception as e:
        logger.error(f"Unexpected scrape error for {url}: {e}")
        return False, str(e)
