"""Structural checks for the language-choice research deliverable.

The repository has no test framework, so these stdlib unittest checks verify the
acceptance criteria of issue #3 against the report itself: all three parts are
present, 30 sentences have two options per candidate language, and the report
has a clear, evidence-backed recommendation with honest evidence status.
"""

import pathlib
import re
import unittest

REPORT = pathlib.Path(__file__).resolve().parents[1] / "language-choice.md"


class LanguageChoiceReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = REPORT.read_text(encoding="utf-8")

    def test_report_exists_and_is_substantial(self):
        self.assertTrue(REPORT.is_file())
        self.assertGreaterEqual(len(self.text.splitlines()), 150)
        self.assertIn("Language choice", self.text)

    def test_all_three_parts_present(self):
        for heading in (
            "## 2. Part 1",
            "## 3. Part 2",
            "## 4. Part 3",
        ):
            self.assertIn(heading, self.text, heading)

    def test_two_candidate_languages_compared(self):
        self.assertIn("Kiswahili", self.text)
        self.assertIn("Hausa", self.text)
        self.assertIn("`sw-KE`", self.text)
        self.assertIn("`ha-NG`", self.text)

    def test_datasets_models_sizes_and_licenses(self):
        for term in (
            "Common Voice",
            "FLEURS",
            "MMS-lab",
            "Whisper",
            "MMS-TTS",
            "Google Cloud STT",
            "Google Cloud TTS",
            "CC0",
            "CC-BY-NC 4.0",
            "MIT",
            "Apache 2.0",
            "AGPL-3.0",
        ):
            self.assertIn(term, self.text, term)
        self.assertRegex(self.text, r"~?3\.1 GB")
        self.assertRegex(self.text, r"~?1\.2 GB")

    def test_android_device_section_has_protocol_and_honest_status(self):
        self.assertIn("checkRecognitionSupport", self.text)
        self.assertIn("getVoices()", self.text)
        self.assertIn("2+ Android phones", self.text)
        self.assertIn("No physical Android device was available", self.text)
        self.assertIn("to be filled", self.text)

    def test_thirty_sentences_with_two_options_each(self):
        rows = {}
        for line in self.text.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 6 and cells[0].isdigit():
                rows[int(cells[0])] = cells
        self.assertEqual(sorted(rows), list(range(1, 31)), "need 30 numbered sentence rows")
        for number, cells in rows.items():
            for index, label in ((2, "Kiswahili A"), (3, "Kiswahili B"),
                                 (4, "Hausa A"), (5, "Hausa B")):
                self.assertTrue(cells[index], f"row {number}: {label} is empty")
            self.assertTrue(cells[1], f"row {number}: English source is empty")

    def test_native_speaker_rubric_and_score_sheet(self):
        self.assertIn("1–5", self.text)
        rubric_section = self.text.split("### 4.2 Rubric", 1)[1].split("### 4.3", 1)[0]
        rubric = re.findall(r"^\| ([1-5]) \|", rubric_section, re.MULTILINE)
        self.assertEqual(sorted(int(v) for v in rubric), [1, 2, 3, 4, 5])
        self.assertIn("Native-speaker score sheet", self.text)
        self.assertIn("not a native speaker", self.text)

    def test_clear_recommendation(self):
        self.assertIn("Language 1 = Kiswahili (Swahili), BCP-47 `sw-KE`", self.text)
        self.assertIn("Handle it directly, not via translation", self.text)
        self.assertIn("Pick Kiswahili (`sw-KE`) as language 1, handled directly", self.text)

    def test_outstanding_human_items_are_declared(self):
        section = self.text.split("## 7. Outstanding human-dependent items", 1)[1]
        self.assertEqual(section.count("- [ ]"), 2)
        self.assertIn("Android device runs", section)
        self.assertIn("Native-speaker scoring", section)

    def test_sources_section_has_urls(self):
        section = self.text.split("## 6. Sources", 1)[1].split("## 7.", 1)[0]
        self.assertGreaterEqual(len(re.findall(r"https://", section)), 10)


if __name__ == "__main__":
    unittest.main()
