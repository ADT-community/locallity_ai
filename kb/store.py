"""Persist and reload the knowledge base index as a plain JSON file."""

import json
import os

from . import ingest

DEFAULT_INDEX_PATH = os.path.join(os.path.dirname(__file__), "index.json")


def save_index(index, path=DEFAULT_INDEX_PATH):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(index, handle, ensure_ascii=False)
    return path


def load_index(path=DEFAULT_INDEX_PATH):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def ensure_index(path=DEFAULT_INDEX_PATH, rebuild=False, **kwargs):
    """Load the committed index, or build and store it when absent/stale."""
    index = None if rebuild else load_index(path)
    if index is None or index.get("version") != ingest.INDEX_VERSION:
        index = ingest.build_index(**kwargs)
        save_index(index, path)
    return index
