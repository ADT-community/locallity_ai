# Language choice — research report

**Issue:** [ADT-community/locallity_ai#3](https://github.com/ADT-community/locallity_ai/issues/3)
**Status:** research complete; two evidence items still require a human (see §7)
**Scope:** choose language 1 for a voice-first assistant for African farmers, with evidence.
**Out of scope:** training models (explicitly excluded by the issue).

## Decision (short version)

**Language 1 = Kiswahili (Swahili), BCP-47 `sw-KE`. Handle it directly, not via translation.**

"Directly" means: the app sends `lang: "sw-KE"` to the phone's built-in `SpeechRecognizer`/`speechSynthesis` first, and our own `sttUrl`/`ttsUrl` endpoints take over where the phone is weak. English↔Swahili translation is a fallback for out-of-scope questions, not the main path.

Why Kiswahili beats the other candidate (Hausa, `ha-NG`):

| Signal | Kiswahili | Hausa | Source |
|---|---|---|---|
| Open speech data (Common Voice 17 derived) | ≈46.5k train + 12.3k test clips (~59k) | ≈1.9k train + 0.7k test clips (~2.6k) | [djelia/multilingual-asr](https://huggingface.co/datasets/djelia/multilingual-asr) |
| Whisper `large-v2` FLEURS WER | 39.3% | 88.9% | [Whisper paper](https://arxiv.org/abs/2212.04356), Appendix D |
| Whisper `large-v3` FLEURS WER | 34.1% | ~86% | [openai/whisper](https://github.com/openai/whisper) |
| Android / Gboard voice typing | supported since 2017 (Tanzania, Kenya) | not in Google's voice-typing rollout | [Google blog](https://blog.google/products-and-platforms/products/search/type-less-talk-more/) |
| Google Cloud TTS voice | `sw-KE` (WaveNet, Neural2, Chirp 3 HD) | **no voice listed** | [Cloud TTS voices](https://docs.cloud.google.com/text-to-speech/docs/list-voices-and-types) |
| Google Cloud STT | `sw`, `sw-KE` (chirp / chirp_2 / chirp_3) | `ha-NG` (chirp / chirp_2 / chirp_3) | [Cloud STT languages](https://docs.cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages) |
| Open TTS model | `facebook/mms-tts-swh` (CC-BY-NC 4.0) | `facebook/mms-tts-hau` (CC-BY-NC 4.0) | [MMS-TTS](https://huggingface.co/facebook/mms-tts-swh) |
| Market reach | East Africa: KE, TZ, UG, RW, BI, CD, MZ (200M+ L1/L2) | West Africa: NG, NE, TD, CM, GH (80M+ L1/L2) | general reference |

The deciding factor is **voice**, not text: Swahili has a commercially usable TTS voice on the phone and in the cloud, plus ~20x more open training audio and roughly half the ASR error rate. Hausa has STT but, as of this writing, **no Google TTS voice**, which breaks the product's core "speak back" loop unless we fund custom TTS.

### Evidence status — read this before treating the report as final

| Item | Status |
|---|---|
| Part 1 (datasets, models, sizes, licenses) | **Complete.** Facts and URLs below; desk research only. |
| Part 2 (2+ Android phones) | **Protocol + platform evidence complete; physical device runs NOT performed.** No Android handset or emulator with Google Play Services was available to this agent, so no per-device result is claimed. The exact test protocol and a fill-in table are in §3. A human with 2 phones must run it. |
| Part 3 (30 sentences, 2 options, native-speaker 1–5) | **Sentences, two candidate renderings per language and the rubric are complete.** The translations are drafts produced by this agent (not a native speaker), so the score column is intentionally blank. A native speaker must score them (§4). |
| Recommendation | **Sound but provisional** until §7 is closed. The platform/data gap is large enough that the expected outcome is unlikely to change. |

No device result or native-speaker score below has been invented. Blank cells mean "not yet measured".

---

## 1. The two candidates

We compare the two African languages that combine large speaker populations with usable open digital resources, and that are already offered in `web/app.js`:

- **Kiswahili (`sw`, app code `sw-KE`)** — East Africa. Linguistically Bantu, Latin script, transparent orthography, standardised variety (Zanzibar/Kiswahili sanifu). It is already the first non-English entry in the app's language picker and the language used in earlier project evaluation work.
- **Hausa (`ha`, app code `ha-NG`)** — West Africa. Afro-Asiatic/Chadic, written in both Latin (Boko) and Ajami scripts. Huge L1 population and a strong open-data community, but far thinner speech resources and weaker phone support.

Other languages in the picker (isiZulu, isiXhosa, Yorùbá, Igbo, Amharic, Kinyarwanda, Somali, Afrikaans) are reasonable **second** languages; they have smaller combined reach or weaker cross-border TTS/STT coverage than these two.

---

## 2. Part 1 — open datasets, models, sizes and licenses

### 2.1 Speech datasets

| Dataset | Kiswahili | Hausa | Size / volume | License | Notes |
|---|---|---|---|---|---|
| [Mozilla Common Voice 17.0](https://commonvoice.mozilla.org/en/datasets) | `sw` — ≈46,494 train + 12,253 test clips in the widely used repackaging | `ha` — ≈1,925 train + 661 test clips | CV-17 total corpus 82.4 GB / 2,615 validated h across all languages; Swahili subset ~20 GB | **CC0** (public domain) | Crowdsourced read speech. Best free ASR starting point. Huge sw/ha imbalance. ([AIMS capstone](https://capstone.aims.ac.za/datasets/common-voice-african/), [HF repackaging](https://huggingface.co/datasets/djelia/multilingual-asr)) |
| [Google FLEURS](https://huggingface.co/datasets/google/fleurs) | `sw_ke`, `sw_tz` | `ha_ng` | ~12 h / ~2k utterances per language | Apache 2.0 | Read speech, 102 languages; good for *evaluation*, too small for training. |
| [Meta MMS-lab](https://github.com/facebookresearch/fairseq/tree/main/examples/mms) | `swh` | `hau` | Part of ~500k h / 1,400+ languages | CC-BY-NC 4.0 (code & weights) | Readings of publicly available religious text; used to train MMS ASR/TTS. Non-commercial only. |
| [Google VoxPopuli](https://github.com/facebookresearch/voxpopuli) | — | — | 400k h, 23 languages | CC0 | Mostly European; **neither** sw nor ha. Listed to show why it is not a candidate source here. |
| [CoVoST 2](https://github.com/facebookresearch/Speech-Translation) | verify per-version coverage | verify per-version coverage | 21 source languages, ~2,900 h | CC-BY 4.0 | Speech *translation* corpus; useful only if sw/ha pairs are present in the release used. |

**Takeaway:** for both languages the only large, clean, commercially usable speech corpus is Common Voice (CC0). It is ~20x bigger for Kiswahili than for Hausa. MMS-lab could close the Hausa gap but its CC-BY-NC license blocks a commercial product.

### 2.2 Text datasets

| Dataset | Kiswahili | Hausa | License | Notes |
|---|---|---|---|---|
| [Wikipedia dumps](https://dumps.wikimedia.org/) | active edition, 100k+ articles | active edition, tens of thousands of articles | CC BY-SA 4.0 + GFDL | Clean encyclopedic text; share-alike obligations apply to derived text. |
| [Common Voice validated sentences](https://commonvoice.mozilla.org/en/datasets) | included | included | CC0 | Short, everyday phrases; good for TTS frontend and prompts. |
| [OSCAR](https://oscar-project.org/) (Common Crawl derived) | present | present | CC-BY-SA 3.0 (verify per release) | Large but noisy web text; filter before use. |
| [NLLB-200 distilled bitext / Masakhane corpora](https://github.com/masakhane-io/masakhane) | present | present | mostly CC-BY-NC 4.0 or CC-BY-SA | Parallel data for the "via translation" option; check each corpus separately. |

**Takeaway:** text is not the bottleneck for either language. Both have Wikipedia, Common Voice sentences and web corpora. Licenses are more permissive for Kiswahili sources in practice (more CC0 material).

### 2.3 Speech-to-text models

| Model | Params / download size | License | Kiswahili | Hausa | Deployability |
|---|---|---|---|---|---|
| [Whisper `large-v3`](https://huggingface.co/openai/whisper-large-v3) | ~1.55B / ~3.1 GB (fp16) | MIT | WER 34.1% (FLEURS) | WER ~86% (FLEURS) | Heavy but runnable on a small server; fine-tune on CV `sw`. |
| Whisper `small` | 244M / ~500 MB | MIT | WER ~73.7% (old FLEURS run) | very poor | Cheap, not good enough for either language without fine-tuning. |
| Whisper `tiny` | 39M / ~75 MB | MIT | WER ~100.9% | unusable | Phone-class size, unacceptable quality. |
| [MMS-1B-all ASR](https://huggingface.co/facebook/mms-1b-all) | ~1B / ~3.9 GB (fp32) | **CC-BY-NC 4.0** | supported (`swh`); 0.087 WER in a Sunbird/SALT fine-tune | supported (`hau`); 0.168 WER in the same fine-tune | 1,162 languages; non-commercial license is a product blocker. |
| MMS-300M | 317M / ~1.2 GB | CC-BY-NC 4.0 | supported | supported | Lighter, same license problem. |
| [Sunbird SALT Whisper-51-African-Languages](https://salt.sunbird.ai/models/asr-whisper-51-african-languages/) | Whisper large-v3 fine-tune | check model card before commercial use | WER 0.087 (99 ex.) | WER 0.168 (287 ex.) | Purpose-built for African languages; strong candidate for `sttUrl`. |
| [Google Cloud STT Chirp 3](https://docs.cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages) | hosted API | proprietary, paid | `sw`, `sw-KE` | `ha-NG` | Best accuracy with zero training; cost/lock-in/data-residency trade-off. |

WER figures are from different evaluations (FLEURS read speech vs. Sunbird's own sets) and are **not** directly comparable to each other. They are consistent in ranking: Swahili is roughly 2–5x easier than Hausa for the same model.

### 2.4 Text-to-speech models

| Model | Size | License | Kiswahili | Hausa | Deployability |
|---|---|---|---|---|---|
| [MMS-TTS `swh`](https://huggingface.co/facebook/mms-tts-swh) | VITS checkpoint, ~100–200 MB | CC-BY-NC 4.0 | available | — | VITS quality, single-speaker; open weights but non-commercial. |
| [MMS-TTS `hau`](https://huggingface.co/facebook/mms-tts-hau) | ~100–200 MB | CC-BY-NC 4.0 | — | available | Same license caveat. |
| [Google Cloud TTS](https://docs.cloud.google.com/text-to-speech/docs/list-voices-and-types) | hosted API | proprietary, paid | `sw-KE`: WaveNet, Neural2, **Chirp 3 HD** | **no Hausa voice listed** | The only turnkey *commercial* natural voice for either candidate. |
| Phone built-in `speechSynthesis` | free | OS-provided | `sw-KE` voice on Android/Google TTS | not generally available | Zero server cost, offline-capable; quality varies by handset (§3). |

### 2.5 License summary

- **Safe for a commercial product:** Common Voice (CC0), FLEURS (Apache 2.0), Whisper weights/code (MIT), Wikipedia/CC BY-SA with attribution+share-alike, Google Cloud APIs (paid).
- **Research / non-commercial only:** all Meta MMS models, NLLB-200, MMS-TTS (`CC-BY-NC 4.0`). These are excellent for prototyping and for the ADT Laptop LLM Challenge, but we cannot ship them in a revenue-generating product without renegotiation or replacement.
- **Product license:** this repository is [AGPL-3.0](../../LICENSE); any new code contributions inherit it. Model licenses are separate from code licenses.

---

## 3. Part 2 — built-in phone speech recognition and voices

### 3.1 What should be tested (protocol for a human tester)

Use **2+ Android phones** from different vendors/price bands, e.g. a mid-range Samsung (One UI, Samsung speech services) and a low-cost phone running stock Android with Google Play Services. For each phone and each locale (`sw-KE`, `sw-TZ`, `ha-NG`):

1. In `web/config.js`, leave `sttUrl` and `ttsUrl` empty so the app uses the phone's own engines; serve `web/` over HTTPS (or `localhost`) and open in Chrome on the phone.
2. Query recognition support programmatically using `SpeechRecognizer.checkRecognitionSupport(intent, executor, callback)` (Android 13+) and record `getInstalledOnDeviceLanguages()`, `getSupportedOnDeviceLanguages()` and `getOnlineLanguages()` ([API](https://developer.android.com/reference/android/speech/RecognitionSupport)). Note `ERROR_LANGUAGE_NOT_SUPPORTED` (12) vs `ERROR_LANGUAGE_UNAVAILABLE` (13) — the latter only needs a model download via `triggerModelDownload`.
3. Read the **same 10 short farming phrases** (a subset of §4) three times each: quiet room, street noise, and with a local accent. Record the transcript verbatim and compute word error rate against the reference.
4. Switch `speechSynthesis` to the locale, list available voices with `getVoices()`, synthesise the same sentences and rate naturalness/intelligibility 1–5.
5. Record latency (tap-to-transcript, text-to-first-audio) and whether recognition worked **offline** (airplane mode).

### 3.2 Platform capability evidence (desk research, available now)

| Capability | Kiswahili | Hausa |
|---|---|---|
| Google voice typing / Gboard | Added in 2017 for Tanzania and Kenya; `sw` is a supported Google speech locale | Not in Google's announced voice-typing locale list; support is inconsistent |
| Android on-device recognition | Locale-dependent; must be queried per handset with `checkRecognitionSupport` | Same, but far less likely to be installed |
| Google TTS voice on device | `sw-KE` voices available via Google TTS | No Google TTS voice listed |
| Cloud STT fallback | `chirp_3` supports `sw`, `sw-KE` | `chirp_3` supports `ha-NG` |
| Cloud TTS fallback | `sw-KE` WaveNet/Neural2/Chirp 3 HD | **none** → would require custom TTS |

Sources: [Android SpeechRecognizer](https://developer.android.com/reference/android/speech/SpeechRecognizer), [RecognitionSupport](https://developer.android.com/reference/android/speech/RecognitionSupport), [Google voice typing announcement](https://blog.google/products-and-platforms/products/search/type-less-talk-more/), [Cloud TTS voices](https://docs.cloud.google.com/text-to-speech/docs/list-voices-and-types), [Cloud STT languages](https://docs.cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages).

### 3.3 Device results table — to be filled by a tester

**No physical Android device was available to the report author. The rows below are deliberately empty; do not read them as passed tests.**

| Phone | OS / speech service | Locale | STT installed / online / downloadable | STT WER (quiet / noise / accent) | TTS voice present | TTS 1–5 | Offline? | Latency |
|---|---|---|---|---|---|---|---|---|
| Phone A (e.g. Samsung mid-range) | | `sw-KE` | | / / | | | | |
| Phone A | | `ha-NG` | | / / | | | | |
| Phone B (e.g. low-cost stock Android) | | `sw-KE` | | / / | | | | |
| Phone B | | `ha-NG` | | / / | | | | |

**Expected outcome from desk evidence:** `sw-KE` recognition and a voice should be present on most Google-serviced handsets; `ha-NG` recognition may be cloud-only or absent, and a Hausa voice is unlikely. If Phone A and Phone B confirm this, ship Kiswahili direct and keep our own STT/TTS endpoints for edge cases.

---

## 4. Part 3 — 30 farming sentences, two options, native-speaker scoring

### 4.1 Method

For each of 30 source sentences (farmer-facing, practical), two candidate renderings are given per language:

- **A — direct phrasing**: natural, idiomatic wording a speaker would actually use.
- **B — alternate/literal phrasing**: closer to the English structure, the kind of output an MT system or a non-native writer tends to produce.

A native speaker scores **each option 1–5** for (a) correctness, (b) naturalness, (c) whether a farmer would understand it immediately. 5 = perfect; 1 = wrong or unintelligible. The gap between A and B tells us how risky "via translation" would be; the absolute scores tell us how much post-editing our own pipeline needs.

**The renderings below are drafts by this agent, who is not a native speaker of Swahili or Hausa. They are hypotheses for a native speaker to judge, not validated translations.**

### 4.2 Rubric

| Score | Meaning |
|---|---|
| 5 | Natural, correct, immediately understood by a farmer; no changes needed. |
| 4 | Correct and clear, slightly awkward or formal. |
| 3 | Understandable but visibly translated; technical term or tone is off. |
| 2 | Partly wrong; meaning survives only with context. |
| 1 | Wrong, nonsense, or uses the wrong language/script. |

### 4.3 Sentences and candidate renderings

| # | English | Kiswahili A | Kiswahili B | Hausa A | Hausa B |
|---|---|---|---|---|---|
| 1 | When should I plant maize? | Ninapaswa kupanda mahindi lini? | Ninapaswa kupanda mahindi wakati gani? | Yaushe zan shuka masara? | A wane lokaci nake shuka masara? |
| 2 | How much fertiliser does one acre need? | Eka moja inahitaji mbolea kiasi gani? | Ni kiasi gani cha mbolea kinachohitajika kwa eka moja? | Eka daya tana bukatar taki nawa? | Nawa ne takin da ake bukata don eka daya? |
| 3 | My cassava leaves are turning yellow. | Majani ya muhogo wangu yanageuka njano. | Majani ya mihogo yangu yanakuwa ya rangi ya njano. | Ganyen rogo na suna rawa rawa. | Ganyen manioc na suna zama rawa. |
| 4 | The rains came late this year. | Mvua ilichelewa mwaka huu. | Mvua ilikuja kwa kuchelewa katika mwaka huu. | Ruwan bana ya zo da jinkiri. | Ruwan wannan shekarar ya zo a makara. |
| 5 | How do I store maize so it does not rot? | Nahifadhije mahindi yasioze? | Ni jinsi gani naweza kuhifadhi mahindi ili yasiharibike? | Yaya zan adana masara don kada ta lalace? | Ta yaya zan ajiye masara domin ba za ta rubuce ba? |
| 6 | When is the best time to spray against fall armyworm? | Ni wakati gani mzuri wa kunyunyizia dawa dhidi ya funza wa jeshi? | Wakati gani ni bora zaidi kwa kunyunyizia dawa kwa minyoo ya jeshi? | Yaushe lokaci mafi kyau na fesa magani ga tsutsar soja? | A wanne lokaci ne mafi alheri a yi feshin maganin tsutsa ta fall armyworm? |
| 7 | My cow is not eating. | Ng'ombe wangu hakili. | Ng'ombe wangu hali chakula. | Saniyata ba ta cin abinci. | Shanu na ba suke cin abinci ba. |
| 8 | How often should I water tomatoes? | Nipaswa kumwagilia nyanya mara ngapi? | Ni mara ngapi ninapaswa kumwagilia nyanya? | Sau nawa nake shayar da tumatur? | Sau nawa ya kamata in shayar da tumatur? |
| 9 | Which seed variety resists drought? | Mbegu ya aina gani inastahimili ukame? | Ni aina gani ya mbegu inayopinga ukame? | Wane irin iri ne ke jure fari? | Wace irin shuka ce take tsayayya da fari? |
| 10 | The price of fertiliser has gone up. | Bei ya mbolea imepanda. | Bei ya mbolea imeongezeka. | Farashin taki ya tashi. | Farashin takin ya karu. |
| 11 | How do I make compost? | Nafanyaje mboji? | Ninatengenezaje mbolea ya kikaboni? | Yaya nake yin takin gargajiya? | Ta yaya nake samar da takin halitta? |
| 12 | My groundnut crop has holes in the leaves. | Majani ya karanga wangu yana mashimo. | Mmea wangu wa karanga una mashimo kwenye majani. | Ganyen gyada na suna da ramuka. | Tsirran gyada na suna da ramuka a ganye. |
| 13 | When is the right time to harvest rice? | Ni wakati gani mzuri wa kuvuna mpunga? | Wakati gani unaofaa wa kusanya mpunga? | Yaushe lokacin girbin shinkafa ya dace? | A wane lokaci ya dace a girbi shinkafa? |
| 14 | How can I keep goats from eating my seedlings? | Nazuaje mbuzi wasile miche yangu? | Ni jinsi gani naweza kuzuia mbuzi kula miche yangu? | Yaya zan hana awaki cin tsirran na? | Ta yaya zan kiyaye akuya daga cin tsirran na? |
| 15 | What can I do about weeds in my field? | Nifanye nini kuhusu magugu shambani? | Ni hatua gani naweza kuchukua kuhusu magugu katika shamba langu? | Me zan yi game da ciyayi a gonata? | Wane mataki zan dauka game da weeds a filin nawa? |
| 16 | My irrigation pump has stopped working. | Pampu yangu ya umwagiliaji imeacha kufanya kazi. | Pampu ya kumwagilia imesimama kufanya kazi. | Famfon din ban ruwa na ya daina aiki. | Injinin shayarwa na ya tsaya aiki. |
| 17 | How much milk does a goat give per day? | Mbuzi hutoa maziwa kiasi gani kwa siku? | Ni kiasi gani cha maziwa mbuzi hutoa kwa siku moja? | Akuya tana ba da madara nawa a rana? | Nawa ne madarar akuya a kowace rana? |
| 18 | Is it safe to use this pesticide on beans? | Je, ni salama kutumia dawa hii kwenye maharagwe? | Ni salama kutumia dawa hii ya wadudu kwenye maharagwe? | Shin lafiya ne a yi amfani da wannan maganin a wake? | Ko yana da aminci a saka wannan maganin a wake? |
| 19 | The soil in my farm is very hard. | Udongo wa shamba langu ni mgumu sana. | Ardhi ya shamba langu ina ugumu mkubwa. | Kasa a gonata tana da tauri sosai. | Filin nawa yana da kasa mai tauri sosai. |
| 20 | How do I dry and store cassava roots? | Nakaushaje na kuhifadhi mizizi ya muhogo? | Ni jinsi gani naweza kukausha na kuhifadhi mizizi ya mihogo? | Yaya nake busarwa da adana tushen rogo? | Ta yaya nake bushewa da ajiye tushen rogo? |
| 21 | I want to join a farmers' group. | Nataka kujiunga na kikundi cha wakulima. | Mimi ninatamani kujiunga na kundi la wakulima. | Ina so in shiga kungiyar manoma. | Ina so na kasance cikin kungiyar masu noma. |
| 22 | What is the weather forecast for next week? | Utabiri wa hali ya hewa wiki ijayo ni upi? | Ni nini utabiri wa hali ya hewa kwa wiki inayokuja? | Menene hasashen yanayi na makonni mai zuwa? | Wane ne hasashen yanayi don mako mai zuwa? |
| 23 | My chickens are not laying eggs. | Kuku wangu hawataji mayai. | Kuku zangu hazize mayai. | Kaji na ba su sa qwai. | Tsuntsayen na ba su yin kwai. |
| 24 | How do I rotate crops on a small plot? | Nazungushaje mazao kwenye eneo dogo? | Ni jinsi gani naweza kubadilisha mazao katika shamba dogo? | Yaya nake juya amfanin gona a ƙaramin fili? | Ta yaya nake canza amfanin gona a karamin fili? |
| 25 | Where can I get a loan for farm inputs? | Naweza kupata mkopo wa pembejeo za kilimo wapi? | Ni wapi naweza kupata mkopo kwa ajili ya pembejeo za shamba? | Ina iya samun lamuni na kayan gona a ina? | A ina zan samu rancen kayan aikin gona? |
| 26 | The market price of maize is low today. | Bei ya mahindi sokoni ni ya chini leo. | Bei ya soko ya mahindi iko chini leo. | Farashin masara a kasuwa yana da ƙasa yau. | Farashin masara a kasuwa ya yi ƙasa a yau. |
| 27 | How do I treat seeds before planting? | Natibuaje mbegu kabla ya kupanda? | Ni jinsi gani natibu mbegu kabla ya kupandwa? | Yaya nake magance iri kafin shuka? | Ta yaya nake kula da iri gabanin shukawa? |
| 28 | My banana plants have black spots. | Mitindi wangu wa ndizi una madoa meusi. | Mimea yangu ya ndizi ina madoa meusi. | Tsirran ayaba na suna da tabo baƙi. | Itatuwan ayaba na suna da tabo masu duhu. |
| 29 | How many kilograms of seed do I need per hectare? | Nahitaji kilo ngapi za mbegu kwa hekta? | Ni kilogiramu ngapi za mbegu ninazohitaji kwa hekta moja? | Nawa kilogiram na iri nake bukata a hekta daya? | Nawa ne kilogiram ɗin irin da ake bukata ga kowace hekta? |
| 30 | Can I sell my produce directly to the school? | Naweza kuuza mazao yangu moja kwa moja kwa shule? | Je, ninaweza kuuza bidhaa zangu moja kwa moja kwa shule? | Zan iya sayar da amfanina kai tsaye ga makaranta? | Ko zan iya sayar da kayan gona na kai tsaye ga makarantar? |

### 4.4 Native-speaker score sheet — to be filled

| # | Kiswahili A (1–5) | Kiswahili B (1–5) | Hausa A (1–5) | Hausa B (1–5) | Notes |
|---|---|---|---|---|---|
| 1–30 | _ | _ | _ | _ | _ |

**Aggregate (pending):** mean A vs B per language, count of scores < 3, and the native speaker's verdict on "direct vs via translation".

The two options are deliberately close to real failure modes (idiom choice, calques, wrong technical term). If a native speaker scores B much lower than A, a naive MT pipeline is not good enough for farming vocabulary and we should keep a human-reviewed glossary of agronomic terms — another argument for direct handling of the chosen language.

---

## 5. Recommendation and rollout

**Pick Kiswahili (`sw-KE`) as language 1, handled directly.**

1. **Now — phone engines.** In `web/config.js` keep `sttUrl`/`ttsUrl` empty; set the default lang to `sw-KE`. The built-in recogniser and `sw-KE` voice give us a free, offline-ish pilot loop. Confirm on the two phones from §3.
2. **Then — our own STT.** Fine-tune an MIT-licensed Whisper (or evaluate the Sunbird African-languages checkpoint, subject to its license) on Common Voice `sw` (CC0). Expose it at `sttUrl`. This fixes noisy markets, accents and farm vocabulary that phone STT misses.
3. **Then — our own TTS alternative.** MMS-TTS `swh` is the quick prototype but is CC-BY-NC 4.0 — do **not** ship it in a paid product. Either license Google Cloud TTS `sw-KE` (fast, commercial, usable now) or train a small voice on CC0/CC BY-SA data for full control. This is the single most important licensing action item.
4. **Translation only as fallback.** Add English↔Swahili translation (NLLB-200 distilled, CC-BY-NC — prototype only, or a licensed API) for questions outside the covered farming domain. Do not translate every turn: it adds latency, cost and compounding errors, and it loses the agronomic vocabulary a native speaker checks in §4.
5. **Second language.** After Kiswahili reaches quality on G1/G2, revisit Hausa. Its blocker is TTS and open speech data; if by then a commercial Hausa voice or a large CC0 Hausa corpus exists, the decision can be reversed cheaply because the architecture is language-agnostic.

**Risks:** phone support varies by handset (§3); ASR WER for Swahili is still ~34% on FLEURS read speech, so design for confirmation/repair ("did you mean…?") rather than trusting a single transcript; MMS/NLLB licenses forbid commercial use — replace before launch.

---

## 6. Sources

- [Common Voice datasets](https://commonvoice.mozilla.org/en/datasets) and [CV-17 release notes](https://discourse.mozilla.org/t/dataset-17-release/128837)
- [AIMS Common Voice African (sw/ha)](https://capstone.aims.ac.za/datasets/common-voice-african/)
- [djelia/multilingual-asr (sw/ha clip counts)](https://huggingface.co/datasets/djelia/multilingual-asr)
- [Google FLEURS](https://huggingface.co/datasets/google/fleurs)
- [OpenAI Whisper repo](https://github.com/openai/whisper) and [paper](https://arxiv.org/abs/2212.04356)
- [Meta MMS project](https://github.com/facebookresearch/fairseq/tree/main/examples/mms), [MMS-1B-all](https://huggingface.co/facebook/mms-1b-all), [MMS-TTS-swh](https://huggingface.co/facebook/mms-tts-swh), [MMS paper](https://jmlr.org/papers/volume25/23-1318/23-1318.pdf)
- [Sunbird SALT Whisper-51 African languages](https://salt.sunbird.ai/models/asr-whisper-51-african-languages/)
- [Google Cloud STT supported languages](https://docs.cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages)
- [Google Cloud TTS voices](https://docs.cloud.google.com/text-to-speech/docs/list-voices-and-types)
- [Android SpeechRecognizer](https://developer.android.com/reference/android/speech/SpeechRecognizer) and [RecognitionSupport](https://developer.android.com/reference/android/speech/RecognitionSupport)
- [Google voice typing announcement (2017)](https://blog.google/products-and-platforms/products/search/type-less-talk-more/)
- [Masakhane](https://github.com/masakhane-io/masakhane), [OSCAR](https://oscar-project.org/), [Wikipedia dumps](https://dumps.wikimedia.org/)

All figures were checked on 2026-11-21. Dataset sizes and model licenses change between releases; re-check the linked pages before committing budget.

---

## 7. Outstanding human-dependent items

These two acceptance items cannot be closed by a desk-research agent and are **not** claimed as done:

- [ ] **Android device runs (§3):** borrow 2 Android phones (different vendors/price bands), run the 5-step protocol, fill the results table. Need: the two devices, ~1 hour, and the app served over HTTPS.
- [ ] **Native-speaker scoring (§4):** have a native speaker of Kiswahili and a native speaker of Hausa score the 60 options 1–5 using the rubric, fill the score sheet, and sign off the verdict. Need: two native speakers (the issue explicitly lists this skill).

Until those boxes are ticked, the report is an evidence-backed proposal for Kiswahili, not a fully validated field study. The data/platform evidence (§2, §3.2) is strong enough to start the Kiswahili work in parallel.
