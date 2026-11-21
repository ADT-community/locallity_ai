"""Tests for grounded replies with a mocked retrieval function."""

import unittest

from kb import api, chat


def fake_result(source_id, title, url, passage, score, license_name="CC BY 4.0"):
    return {
        "passage": passage,
        "source": title,
        "title": title,
        "url": url,
        "score": score,
        "source_id": source_id,
        "publisher": "FAO",
        "license": license_name,
        "topic": "Maize",
        "country": "Kenya",
    }


def search_with_results(question, k=5):
    return [
        fake_result("maize", "Maize manual", "https://example.org/maize",
                    "Plant maize at the start of the rains. Thin seedlings early. " * 4, 0.82),
        fake_result("cowpea", "Cowpea guide", "https://example.org/cowpea",
                    "Rotate cereals with cowpea to restore soil nitrogen. " * 4, 0.61),
    ]


class MockedSearchTests(unittest.TestCase):
    def test_reply_cites_each_source(self):
        result = chat.answer("When should I plant maize?", search_fn=search_with_results)
        self.assertIn("[1]", result["reply"])
        self.assertIn("[2]", result["reply"])
        self.assertIn("Sources:", result["reply"])
        self.assertEqual([source["url"] for source in result["sources"]],
                         ["https://example.org/maize", "https://example.org/cowpea"])
        self.assertEqual(len(result["passages"]), 2)
        self.assertIn("CC BY 4.0", result["reply"])

    def test_duplicate_chunks_from_one_source_get_one_citation(self):
        def duplicated(question, k=5):
            return [search_with_results(question, k)[0],
                    fake_result("maize", "Maize manual", "https://example.org/maize",
                                "Harvest when the grain is dry.", 0.55)]

        result = chat.answer(" maize storage ", search_fn=duplicated)
        self.assertEqual(len(result["sources"]), 1)
        self.assertNotIn("[2]", result["reply"].split("Sources:")[0])

    def test_empty_search_gives_no_invented_advice(self):
        result = chat.answer("unknown topic", search_fn=lambda question, k=5: [])
        self.assertIn("I don't know", result["reply"])
        self.assertNotIn("Sources:", result["reply"])
        self.assertEqual(result["sources"], [])

    def test_health_questions_defer_to_professional(self):
        result = chat.answer("My child has malaria, what medicine should I give?",
                             search_fn=search_with_results)
        self.assertIn("health professional", result["reply"])
        self.assertTrue(result["sources"])

    def test_chat_handler_uses_last_user_message(self):
        seen = {}

        def recording_search(question, k=5):
            seen["question"] = question
            seen["k"] = k
            return search_with_results(question, k)

        payload = {
            "lang": "en", "k": 2,
            "messages": [{"role": "user", "content": "hello"},
                         {"role": "user", "content": "How do I plant maize?"}],
        }
        result = api.handle_chat(payload, search_fn=recording_search)
        self.assertEqual(seen, {"question": "How do I plant maize?", "k": 2})
        self.assertEqual(result["sources"], ["https://example.org/maize",
                                             "https://example.org/cowpea"])
        self.assertEqual(result["citations"][0]["license"], "CC BY 4.0")

    def test_chat_handler_accepts_question_field(self):
        seen = {}

        def recording_search(question, k=5):
            seen["question"] = question
            return []

        result = api.handle_chat({"question": "groundnut rotation"},
                                 search_fn=recording_search)
        self.assertEqual(seen["question"], "groundnut rotation")
        self.assertEqual(result["sources"], [])

    def test_chat_handler_validates(self):
        with self.assertRaises(ValueError):
            api.handle_chat([])
        with self.assertRaises(ValueError):
            api.handle_chat({"question": "maize", "k": 0})

    def test_handler_with_real_kb(self):
        result = api.handle_chat({"question": "How do I control fall armyworm?"})
        self.assertTrue(result["sources"])
        self.assertTrue(all(url.startswith("https://") for url in result["sources"]))
        self.assertIn("[1]", result["reply"])


if __name__ == "__main__":
    unittest.main()
