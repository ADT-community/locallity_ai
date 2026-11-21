"""Retrieval over the indexed knowledge base: ``search(question, k=5)``."""

from . import store
from .embeddings import backend_from_state, cosine

_kb = None


class KnowledgeBase:
    """In-memory index that returns passages with source links and scores."""

    def __init__(self, index):
        self.index = index
        self.documents = index["documents"]
        self.embeddings = index["embeddings"]
        self.backend = backend_from_state(index["backend"])

    @classmethod
    def load(cls, path=None, **kwargs):
        return cls(store.ensure_index(path, **kwargs) if path else store.ensure_index(**kwargs))

    def search(self, question, k=5, min_score=0.0):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string")
        if not isinstance(k, int) or k < 1:
            raise ValueError("k must be a positive integer")
        vector = self.backend.embed([question])[0]
        scores = [(cosine(vector, embedding), position)
                  for position, embedding in enumerate(self.embeddings)]
        scores = [(score, position) for score, position in scores if score >= min_score]
        scores.sort(key=lambda item: (-item[0], item[1]))
        results = []
        for score, position in scores[:k]:
            document = self.documents[position]
            results.append({
                "passage": document["text"],
                "source": document["title"],
                "title": document["title"],
                "url": document["url"],
                "score": round(score, 6),
                "source_id": document["id"],
                "chunk_id": document["chunk_id"],
                "publisher": document["publisher"],
                "license": document["license"],
                "topic": document["topic"],
                "country": document["country"],
            })
        return results

    def size(self):
        return len(self.documents)


def get_kb():
    global _kb
    if _kb is None:
        _kb = KnowledgeBase.load()
    return _kb


def set_kb(instance):
    global _kb
    _kb = instance
    return instance


def search(question, k=5, min_score=0.0):
    """Return the top-k passages with source links for *question*."""
    return get_kb().search(question, k=k, min_score=min_score)
