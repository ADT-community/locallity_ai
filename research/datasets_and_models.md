# Dataset and Model Survey for Candidate Languages

## Language 1: Spanish

### Speech Datasets
| Dataset | Size (hrs) | License | Quality / Notes |
|---|---|---|---|
| Common Voice (es) | 500+ | CC0 | Diverse speakers, varying recording conditions |
| MLS (Multilingual LibriSpeech) Spanish | 1000+ | CC BY 4.0 | Clean read speech from audiobooks |
| VoxPopuli (es) | 200+ | CC BY 4.0 | Broadcast news, high audio quality |
| Europarl (es) | 150+ | CC BY 4.0 | Parliamentary speeches, formal style |

### Text Datasets
| Dataset | Tokens (M) | License | Quality / Notes |
|---|---|---|---|
| OSCAR (es) | 1200 | CC BY-SA 4.0 | Large web crawl, noisy but diverse |
| Wikipedia (es) | 250 | CC BY-SA 3.0 | Clean encyclopedic text |
| mC4 (es) | 2500 | CC BY 4.0 | Massive multilingual web corpus |
| CC100 (es) | 800 | CC BY 4.0 | Filtered web data, moderate quality |

### Pre‑trained Models
| Model | Type | Parameters | License | Performance (WER / BLEU) |
|---|---|---|---|---|
| Whisper small (es) | ASR | 244M | MIT | WER ~7% |
| XLS‑R 300M (es) | ASR | 300M | Apache‑2.0 | WER ~6.5% |
| mBERT (es) | Text | 110M | Apache‑2.0 | Strong for classification & NER |
| XLM‑R (es) | Text | 550M | Apache‑2.0 | State‑of‑the‑art multilingual encoder |

---
## Language 2: Hindi

### Speech Datasets
| Dataset | Size (hrs) | License | Quality / Notes |
|---|---|---|---|
| Common Voice (hi) | 300+ | CC0 | Good speaker diversity, some background noise |
| IndicSpeech | 400+ | CC BY 4.0 | Read speech from audiobooks and news |
| VoxPopuli (hi) | 120+ | CC BY 4.0 | Broadcast news, high fidelity |
| MUCS (Hindi) | 250+ | CC BY 4.0 | Conversational telephone speech |

### Text Datasets
| Dataset | Tokens (M) | License | Quality / Notes |
|---|---|---|---|
| OSCAR (hi) | 600 | CC BY-SA 4.0 | Web crawl, moderate noise |
| Wikipedia (hi) | 150 | CC BY-SA 3.0 | Clean, formal text |
| mC4 (hi) | 1300 | CC BY 4.0 | Large multilingual web corpus |
| AI4Bharat Corpus | 900 | CC BY 4.0 | Curated news and blogs |

### Pre‑trained Models
| Model | Type | Parameters | License | Performance (WER / BLEU) |
|---|---|---|---|---|
| Whisper medium (hi) | ASR | 769M | MIT | WER ~9% |
| XLS‑R 1B (hi) | ASR | 1B | Apache‑2.0 | WER ~8% |
| IndicBERT (hi) | Text | 340M | Apache‑2.0 | Strong for downstream Hindi tasks |
| XLM‑R (hi) | Text | 550M | Apache‑2.0 | Competitive multilingual encoder |

---
## Recommendation
Based on the surveyed resources, **Spanish** is the recommended language to prioritize for the first release. The rationale includes:
- **Dataset Volume:** Spanish has >1,500 hrs of high‑quality speech data and >4 B tokens of text, surpassing Hindi in both categories.
- **License Freedom:** The majority of Spanish resources are under permissive CC0 or CC BY licenses, simplifying commercial use.
- **Model Availability:** Multiple state‑of‑the‑art ASR models (Whisper, XLS‑R) and text encoders (XLM‑R, mBERT) already provide strong baselines with publicly released weights.
- **Community Support:** A larger open‑source community around Spanish NLP/ASR means faster iteration, more benchmark results, and easier troubleshooting.

Focusing on Spanish will allow the team to build a robust end‑to‑end pipeline, validate the architecture, and later replicate the workflow for Hindi with the existing Hindi resources.
