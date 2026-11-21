Closes #3

## Language research: pick our first language

Deliverable added at the exact requested path: `docs/research/language-choice.md`.

### Recommendation

**Language 1 = Kiswahili (Swahili), `sw-KE`, handled directly — not via translation.** The only other serious candidate compared is Hausa (`ha-NG`).

Evidence used (all linked in the report):

- **Open speech data:** Common Voice 17 gives Kiswahili ≈46.5k train + 12.3k test clips vs. Hausa ≈1.9k + 0.7k (CC0). FLEURS and MMS-lab cover both.
- **Models and sizes:** Whisper large-v3 (1.55B, ~3.1 GB, MIT), Whisper small/tiny, MMS-1B-all (1B, ~3.9 GB, CC-BY-NC 4.0), MMS-TTS `swh`/`hau` (VITS, CC-BY-NC 4.0), Google Cloud STT (Chirp 3) and TTS.
- **Accuracy:** Whisper large-v2 FLEURS WER 39.3% (Swahili) vs 88.9% (Hausa); large-v3 34.1% vs ~86%.
- **Phones:** Swahili has had Google voice typing since 2017 and a `sw-KE` cloud/on-device TTS voice; Hausa has STT (`ha-NG`) but **no Google TTS voice** — that breaks the speak-back loop.
- **Licensing:** MMS/NLLB are CC-BY-NC 4.0 and cannot ship in a paid product; the rollout plan uses CC0/Apache/MIT sources or a licensed cloud TTS.

### The three required parts

1. **Datasets / models / sizes / licenses** — §2, with per-language tables for speech data, text data, STT and TTS.
2. **Android phone testing** — §3 contains the reproducible 5-step protocol (SpeechRecognizer API, 10 phrases x 3 conditions, latency/offline/TTS checks), desk evidence from Android/Google docs, and a results table for 2+ phones.
3. **30 farming sentences, 2 options, 1–5 scoring** — §4 has all 30 English sentences with two candidate renderings each for **both** Kiswahili and Hausa (120 renderings), a 1–5 rubric and a score sheet.

### Honest limitations

Two acceptance items genuinely require a human and are **not claimed as done** (documented in §7 of the report):

- No Android handset / emulator was available to this agent, so no per-device results are fabricated — the fill-in table and protocol are provided. A tester with 2 phones must run it (~1 hour).
- The renderings in §4 are drafts by a non-native speaker, so the native-speaker score column is blank. A Kiswahili and a Hausa native speaker must score 60 options 1–5.

The recommendation is still actionable because the data and platform advantage of Kiswahili is large; the report lists both gaps as explicit follow-ups rather than hiding them.

### Checks

```
python -m unittest discover -s docs/research/tests -v
Ran 10 tests ... OK
python -m py_compile docs/research/tests/test_language_choice.py   (no errors)
```

The 10 stdlib tests validate the acceptance criteria against the report: all three parts, two named candidates, dataset/model/licence coverage, Android protocol + honest status, 30 numbered sentences with two non-empty options per language, the 1–5 rubric and score sheet, an unambiguous recommendation, the two declared human items, and ≥10 source URLs.

Only `docs/` and this PR body were added; no app code was touched.
