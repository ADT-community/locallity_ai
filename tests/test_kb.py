"""Tests for sources, indexing, embeddings, retrieval and evaluation evidence."""

import os
import tempfile
import unittest

from kb import chat, ingest, search, store
from kb.embeddings import HashingEmbedding, cosine
from kb.search import KnowledgeBase

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SourceTests(unittest.TestCase):
    def test_sources_have_required_metadata(self):
        sources = ingest.load_sources(os.path.join(ROOT, "kb", "sources.csv"))
        self.assertGreaterEqual(len(sources), 20)
        for source in sources:
            for column in ingest.REQUIRED_COLUMNS:
                self.assertTrue(source[column].strip(), "%s: %s" % (source["id"], column))
            self.assertTrue(source["url"].startswith("https://"))
            self.assertTrue(source["license"].strip())

    def test_every_source_has_document(self):
        sources = ingest.load_sources(os.path.join(ROOT, "kb", "sources.csv"))
        for source in sources:
            document = ingest.load_document(source["id"], os.path.join(ROOT, "kb", "documents"))
            self.assertGreater(len(document.split()), 50, source["id"])


class ChunkingTests(unittest.TestCase):
    def test_overlapping_windows(self):
        words = ["w%d" % number for number in range(250)]
        chunks = ingest.chunk_text(" ".join(words), size=100, overlap=20)
        self.assertEqual(len(chunks), 4)
        self.assertEqual(chunks[0].split()[:3], words[:3])
        self.assertEqual(chunks[1].split()[:5], words[80:85])
        self.assertTrue(all(chunk.split() for chunk in chunks))

    def test_short_text_and_invalid_options(self):
        self.assertEqual(ingest.chunk_text("one two three"), ["one two three"])
        self.assertEqual(ingest.chunk_text("   "), [])
        with self.assertRaises(ValueError):
            ingest.chunk_text("a b c", size=10, overlap=10)


class EmbeddingTests(unittest.TestCase):
    def test_deterministic_and_ranked(self):
        texts = ["maize planting spacing and fertilizer in Tanzania",
                 "cowpea pods and Striga in West Africa"]
        backend = HashingEmbedding(dimension=512).fit(texts)
        first = backend.embed([texts[0]])[0]
        self.assertEqual(first, backend.embed([texts[0]])[0])
        self.assertAlmostEqual(sum(value * value for value in first), 1.0, places=6)
        query = backend.embed(["maize planting in Tanzania"])[0]
        self.assertGreater(cosine(query, first),
                           cosine(query, backend.embed([texts[1]])[0]))

    def test_state_roundtrip(self):
        backend = HashingEmbedding(dimension=256).fit(["groundnut rotation and phosphorus"])
        restored = HashingEmbedding.from_state(backend.state())
        self.assertEqual(restored.embed(["groundnut"]), backend.embed(["groundnut"]))


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = ingest.build_index()
        cls.kb = KnowledgeBase(cls.index)

    def test_index_shape(self):
        self.assertGreater(self.kb.size(), 20)
        self.assertEqual(len(self.index["embeddings"]), len(self.index["documents"]))
        self.assertEqual(self.index["version"], ingest.INDEX_VERSION)

    def test_search_returns_passages_with_source_links(self):
        results = self.kb.search("How do I control fall armyworm on maize?", k=5)
        self.assertEqual(len(results), 5)
        self.assertTrue(all(result["passage"] and result["url"].startswith("https://")
                            for result in results))
        self.assertTrue(all(isinstance(result["score"], float) for result in results))
        scores = [result["score"] for result in results]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(len({result["chunk_id"] for result in results}), 5)
        self.assertTrue(any("armyworm" in result["passage"].lower() for result in results))

    def test_search_relevant_to_other_topics(self):
        cowpea = self.kb.search("When should I sow cowpea in West Africa?", k=5)
        self.assertTrue(any("cowpea" in result["passage"].lower() for result in cowpea))

    def test_k_bounds_and_validation(self):
        self.assertLessEqual(len(self.kb.search("maize", k=1000)), self.kb.size())
        with self.assertRaises(ValueError):
            self.kb.search("maize", k=0)
        with self.assertRaises(ValueError):
            self.kb.search("")

    def test_min_score_filters_weak_matches(self):
        results = self.kb.search("zzzqxx nothing matches", k=5, min_score=0.99)
        self.assertEqual(results, [])

    def test_module_level_search(self):
        search.set_kb(self.kb)
        self.assertEqual(len(search.search("groundnut soil", k=3)), 3)

    def test_store_roundtrip(self):
        handle, path = tempfile.mkstemp(suffix=".json")
        os.close(handle)
        try:
            store.save_index(self.index, path)
            loaded = store.load_index(path)
            self.assertEqual(loaded["settings"], self.index["settings"])
            self.assertEqual(KnowledgeBase(loaded).search("maize", k=2)[0]["title"],
                             self.kb.search("maize", k=2)[0]["title"])
        finally:
            os.remove(path)


class EvaluationTests(unittest.TestCase):
    def test_ten_questions_with_recorded_results(self):
        from kb import evaluate

        questions = evaluate.load_questions()
        self.assertEqual(len(questions), 10)
        self.assertTrue(all(item["question"] and item["topic"] for item in questions))
        with open(evaluate.RESULTS_FILE, encoding="utf-8") as handle:
            results = handle.read()
        self.assertEqual(results.count("\n## "), 10)
        self.assertIn("https://", results)


class GroundedAnswerTests(unittest.TestCase):
    def test_search_failure_is_not_silently_invented(self):
        result = chat.answer("anything", search_fn=lambda question, k=5: [])
        self.assertIn("I don't know", result["reply"])
        self.assertEqual(result["sources"], [])


if __name__ == "__main__":
    unittest.main()
