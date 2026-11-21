"""Load curated sources, split guide summaries into chunks and build a search index."""

import csv
import os

from .embeddings import get_backend

DEFAULT_CSV = os.path.join(os.path.dirname(__file__), "sources.csv")
DEFAULT_DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")
REQUIRED_COLUMNS = ("id", "title", "url", "publisher", "license", "topic", "country")
INDEX_VERSION = 1


def load_sources(csv_path=DEFAULT_CSV):
    with open(csv_path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    missing = [column for column in REQUIRED_COLUMNS if not rows or column not in rows[0]]
    if missing:
        raise ValueError("sources.csv is missing required columns: %s" % ", ".join(missing))
    for row in rows:
        if not row["url"].startswith(("http://", "https://")):
            raise ValueError("invalid source URL for %s" % row["id"])
        if not row["license"].strip():
            raise ValueError("missing license for %s" % row["id"])
    return rows


def load_document(source_id, documents_dir=DEFAULT_DOCUMENTS_DIR):
    path = os.path.join(documents_dir, source_id + ".txt")
    with open(path, encoding="utf-8") as handle:
        text = handle.read().strip()
    if not text:
        raise ValueError("empty document: %s" % path)
    return text


def chunk_text(text, size=120, overlap=20):
    """Split text into overlapping word windows."""
    if size < 1 or overlap < 0 or overlap >= size:
        raise ValueError("require size >= 1 and 0 <= overlap < size")
    words = text.split()
    if not words:
        return []
    step = size - overlap
    return [" ".join(words[start : start + size]) for start in range(0, len(words), step)]


def build_index(csv_path=DEFAULT_CSV, documents_dir=DEFAULT_DOCUMENTS_DIR,
                backend=None, chunk_size=120, overlap=20):
    """Build an embedding index from the curated CSV and local guide summaries."""
    sources = load_sources(csv_path)
    backend = backend or get_backend()
    chunks = []
    for source in sources:
        for position, text in enumerate(chunk_text(load_document(source["id"], documents_dir),
                                                   chunk_size, overlap)):
            record = dict(source)
            record["chunk_id"] = "%s:%d" % (source["id"], position)
            record["text"] = text
            chunks.append(record)
    if not chunks:
        raise ValueError("no chunks to index")
    search_texts = [
        " ".join([chunk["text"]] + [chunk["title"]] * 3 + [chunk["topic"]] * 3)
        for chunk in chunks
    ]
    backend.fit(search_texts)
    return {
        "version": INDEX_VERSION,
        "backend": backend.state(),
        "settings": {"chunk_size": chunk_size, "overlap": overlap},
        "documents": chunks,
        "embeddings": backend.embed(search_texts),
    }
