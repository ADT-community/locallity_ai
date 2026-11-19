import os
import pandas as pd
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util

# Constants
CHUNK_SIZE_WORDS = 200  # Approximate size of each text chunk
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class KnowledgeBase:
    """Loads sources, creates text chunks, embeds them, and provides similarity search."""

    def __init__(self, csv_path: str = None):
        self.csv_path = csv_path or os.path.join(os.path.dirname(__file__), "..", "kb", "sources.csv")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self._load_and_prepare()

    def _load_and_prepare(self):
        # Load CSV – expected columns: source, url, text
        df = pd.read_csv(self.csv_path)
        required_cols = {"source", "url", "text"}
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            raise ValueError(f"sources.csv is missing required columns: {missing}")

        # Split each document into chunks
        chunks = []
        meta = []  # Parallel list storing source and url for each chunk
        for _, row in df.iterrows():
            source = row["source"]
            url = row["url"]
            text = str(row["text"]).strip()
            for chunk in self._split_into_chunks(text):
                chunks.append(chunk)
                meta.append({"source": source, "url": url})

        self.chunks = chunks
        self.meta = meta
        # Compute embeddings once
        self.embeddings = self.model.encode(self.chunks, convert_to_tensor=True, show_progress_bar=False)

    @staticmethod
    def _split_into_chunks(text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), CHUNK_SIZE_WORDS):
            chunk_words = words[i : i + CHUNK_SIZE_WORDS]
            chunks.append(" ".join(chunk_words))
        return chunks

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Return the top‑k most similar chunks for *query*.

        Each result dict contains:
        - ``passage`` – the text chunk
        - ``source`` – name of the original source
        - ``url`` – link to the source
        - ``score`` – cosine similarity (0‑1)
        """
        query_emb = self.model.encode(query, convert_to_tensor=True)
        # Compute cosine similarities
        cos_scores = util.cos_sim(query_emb, self.embeddings)[0]
        # Get top‑k indices
        top_results = np.argpartition(-cos_scores.cpu().numpy(), range(k))[:k]
        # Sort those top results by actual score descending
        top_results = top_results[np.argsort(-cos_scores.cpu().numpy()[top_results])]
        results = []
        for idx in top_results:
            results.append(
                {
                    "passage": self.chunks[idx],
                    "source": self.meta[idx]["source"],
                    "url": self.meta[idx]["url"],
                    "score": float(cos_scores[idx].cpu().numpy()),
                }
            )
        return results


# Global instance for convenience
_kb_instance = KnowledgeBase()


def search(question: str, k: int = 5) -> List[Dict]:
    """Public API used by the rest of the project.

    Example:
    ```python
    from api.search import search
    results = search("How do I prevent powdery mildew on tomatoes?", k=3)
    for r in results:
        print(r["passage"], r["source"], r["url"], r["score"])
    ```
    """
    return _kb_instance.search(question, k)
