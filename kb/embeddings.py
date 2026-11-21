"""Deterministic local embeddings, with an optional sentence-transformers backend."""

import hashlib
import math
import re

STOPWORDS = frozenset(
    """a an and are as at be been but by for from had has have how i in into is it its
    of on or our that the their them then there these they this to was were what when
    where which who why will with would you your about can could do does did not no
    please tell me give suggest need want""".split()
)

_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
_SUFFIXES = ("ing", "edly", "ed", "ies", "es", "s")


def tokenize(text):
    """Lowercase, split into words, drop stopwords and apply a light stem."""
    tokens = []
    for raw in _TOKEN_RE.findall(text.lower()):
        if len(raw) < 2 or raw in STOPWORDS or raw.isdigit():
            continue
        stem = raw
        for suffix in _SUFFIXES:
            if stem.endswith(suffix) and len(stem) - len(suffix) >= 3:
                stem = stem[: -len(suffix)]
                break
        if stem.endswith("y") and len(stem) > 3:
            stem = stem[:-1] + "i"
        tokens.append(stem)
    tokens.extend("%s_%s" % (left, right) for left, right in zip(tokens, tokens[1:]))
    return tokens


class HashingEmbedding:
    """Signed feature hashing with corpus IDF weights and L2 normalisation."""

    name = "hashing"

    def __init__(self, dimension=2048):
        if dimension < 16:
            raise ValueError("dimension must be at least 16")
        self.dimension = dimension
        self.idf = {}

    def fit(self, texts):
        doc_freq = {}
        total = 0
        for text in texts:
            total += 1
            for token in set(tokenize(text)):
                doc_freq[token] = doc_freq.get(token, 0) + 1
        self.idf = {
            token: math.log((1.0 + total) / (1.0 + freq)) + 1.0
            for token, freq in doc_freq.items()
        }
        return self

    def _bucket(self, token):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        number = int.from_bytes(digest, "big")
        return number % self.dimension, 1.0 if number & 1 else -1.0

    def embed(self, texts):
        default_weight = math.log(2.0) + 1.0
        vectors = []
        for text in texts:
            vector = [0.0] * self.dimension
            for token in tokenize(text):
                index, sign = self._bucket(token)
                vector[index] += sign * self.idf.get(token, default_weight)
            norm = math.sqrt(sum(value * value for value in vector))
            if norm:
                vector = [value / norm for value in vector]
            vectors.append(vector)
        return vectors

    def state(self):
        return {"name": self.name, "dimension": self.dimension, "idf": self.idf}

    @classmethod
    def from_state(cls, state):
        backend = cls(dimension=state["dimension"])
        backend.idf = state["idf"]
        return backend


class SentenceTransformerEmbedding:
    """Optional real embedding backend; imported only when explicitly selected."""

    name = "sentence-transformers"

    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def fit(self, texts):
        return self

    def embed(self, texts):
        vectors = self.model.encode(list(texts), convert_to_numpy=True, show_progress_bar=False)
        return [normalise([float(value) for value in vector]) for vector in vectors]

    def state(self):
        return {"name": self.name, "model": self.model_name}

    @classmethod
    def from_state(cls, state):
        return cls(model_name=state["model"])


def normalise(vector):
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else list(vector)


def cosine(left, right):
    return sum(a * b for a, b in zip(left, right))


def get_backend(name="hashing", **kwargs):
    if name == HashingEmbedding.name:
        return HashingEmbedding(**kwargs)
    if name == SentenceTransformerEmbedding.name:
        return SentenceTransformerEmbedding(**kwargs)
    raise ValueError("unknown embedding backend: %s" % name)


def backend_from_state(state):
    name = state["name"]
    if name == HashingEmbedding.name:
        return HashingEmbedding.from_state(state)
    if name == SentenceTransformerEmbedding.name:
        return SentenceTransformerEmbedding.from_state(state)
    raise ValueError("unknown embedding backend: %s" % name)
