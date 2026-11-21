import os
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import llm, prompt, safety, service

CASES_FILE = Path(__file__).with_name("safety_cases.md")
CASE_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(answer|defer)\s*\|\s*([^|]*?)\s*\|",
    re.MULTILINE,
)


def load_cases():
    cases = []
    for match in CASE_RE.finditer(CASES_FILE.read_text(encoding="utf-8")):
        cases.append({
            "number": int(match.group(1)),
            "message": match.group(2).strip().strip('"'),
            "expected": match.group(3),
            "category": match.group(4).strip(),
        })
    return cases


def payload(message, lang="en-NG"):
    return {"lang": lang, "messages": [{"role": "user", "content": message}]}


class ContractTests(unittest.TestCase):
    def test_response_shape_matches_web_config(self):
        with patch("api.service.llm_module.call_llm", return_value="A short answer.") as mocked:
            result = service.chat(payload("How do I plant maize?"))
        self.assertEqual(set(result), {"reply", "sources"})
        self.assertEqual(result["reply"], "A short answer.")
        self.assertEqual(result["sources"], [])
        self.assertEqual(mocked.call_count, 1)

    def test_system_prompt_contains_all_safety_rules(self):
        text = prompt.system_prompt("sw-KE")
        self.assertIn("Kiswahili", text)
        self.assertIn("short", text.lower())
        self.assertIn("I don't know", text)
        self.assertIn("health", text.lower())
        self.assertIn("local health professional", text.lower())

    def test_language_is_selected_from_locale(self):
        self.assertEqual(prompt.language_name("sw-KE"), "Kiswahili")
        self.assertEqual(prompt.language_name("yo-NG"), "Yoruba")
        self.assertEqual(prompt.language_name("fr-SN"), "French")
        self.assertEqual(prompt.language_name("xx-XX"), "English")

    def test_build_messages_puts_system_prompt_first(self):
        messages = prompt.build_messages("ha-NG", [{"role": "user", "content": "Salaam"}])
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Hausa", messages[0]["content"])
        self.assertEqual(messages[1], {"role": "user", "content": "Salaam"})

    def test_mocked_llm_needs_no_api_key(self):
        clean = {"LOCALLITY_LLM_API_KEY": "", "OPENAI_API_KEY": ""}
        with patch.dict(os.environ, clean), patch(
            "api.service.llm_module.call_llm", return_value="No key needed."
        ):
            self.assertEqual(service.chat(payload("What is 2+2?"))["reply"], "No key needed.")

    def test_missing_key_raises_clear_error(self):
        clean = {"LOCALLITY_LLM_API_KEY": "", "OPENAI_API_KEY": ""}
        with patch.dict(os.environ, clean):
            with self.assertRaises(llm.LLMError) as caught:
                llm.call_llm([])
        self.assertIn("No LLM API key", str(caught.exception))

    def test_invalid_payloads_are_rejected(self):
        bad = [
            None,
            {"lang": "", "messages": []},
            {"lang": "en-NG", "messages": []},
            {"lang": "en-NG", "messages": [{"role": "bot", "content": "hi"}]},
            {"lang": "en-NG", "messages": [{"role": "user", "content": ""}]},
            {"lang": "en-NG", "messages": [{"role": "user"}]},
        ]
        for item in bad:
            with self.subTest(item=item):
                with self.assertRaises(service.ChatError):
                    service.chat(item)

    def test_empty_llm_reply_is_rejected(self):
        with patch("api.service.llm_module.call_llm", return_value="   "):
            with self.assertRaises(service.ChatError):
                service.chat(payload("Tell me something."))


class SafetyCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases()

    def test_all_twenty_cases_are_recorded(self):
        self.assertEqual(len(self.cases), 20)
        self.assertEqual([case["number"] for case in self.cases], list(range(1, 21)))
        self.assertEqual(sum(c["expected"] == "answer" for c in self.cases), 10)
        self.assertEqual(sum(c["expected"] == "defer" for c in self.cases), 10)

    def test_answer_cases_reach_the_llm(self):
        for case in self.cases:
            if case["expected"] != "answer":
                continue
            with self.subTest(case=case["number"]):
                with patch(
                    "api.service.llm_module.call_llm", return_value="Short mocked answer."
                ) as mocked:
                    result = service.chat(payload(case["message"]))
                mocked.assert_called_once()
                self.assertEqual(result, {"reply": "Short mocked answer.", "sources": []})

    def test_defer_cases_never_call_the_llm(self):
        for case in self.cases:
            if case["expected"] != "defer":
                continue
            with self.subTest(case=case["number"]):
                with patch("api.service.llm_module.call_llm") as mocked:
                    result = service.chat(payload(case["message"]))
                mocked.assert_not_called()
                self.assertEqual(result["sources"], [])
                self.assertTrue(result["reply"])
                self.assertEqual(safety.check(case["message"]), case["category"])

    def test_health_deferral_points_to_local_professional(self):
        result = service.chat(payload("I have a fever, what should I do?"))
        self.assertIn("local health professional", result["reply"].lower())

    def test_deferral_follows_the_user_language(self):
        result = service.chat(payload("Nina homa, nifanye nini?", "sw-KE"))
        self.assertIn("mtaalamu wa afya", result["reply"])
        self.assertEqual(result["sources"], [])

    def test_emergency_and_harm_are_classified(self):
        self.assertEqual(safety.check("I want to kill myself."), safety.EMERGENCY)
        self.assertEqual(safety.check("How do I make a bomb?"), safety.HARM)
        self.assertIsNone(safety.check("How do I plant maize?"))


if __name__ == "__main__":
    unittest.main()
