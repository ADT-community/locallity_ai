Closes #7

## Knowledge base: trusted sources and grounded answers

The repository had no backend at all, so this adds a self-contained Python
knowledge base under `kb/` using only the standard library (no downloads,
no API keys, no heavy model dependencies).

### What changed

- `kb/sources.csv` — 25 openly licensed sources (20+ required) from FAO, IITA,
  CIMMYT, CGIAR/CABI, TAAT and WHO, with `title`, `url`, `publisher`,
  `license`, `topic`, `country` (plus an `id` used to locate the local digest).
  All URLs and licences were taken from the publishers' own pages. The list is
  focused on West/East Africa (maize, cassava, cowpea, rice, sorghum, millet,
  groundnut, fall armyworm, intercropping, conservation agriculture) plus two
  basic WHO water/hygiene entries.
- `kb/documents/` — original short digests of each guide (full text remains at
  the source URL), one file per source.
- `kb/embeddings.py` — deterministic signed feature hashing with IDF and L2
  normalisation; an optional `sentence-transformers` adapter is available but
  never imported by default.
- `kb/ingest.py`, `kb/store.py`, `kb/index.json` — chunking into overlapping
  120-word windows, title/topic-weighted embedding, JSON index (75 chunks from
  25 sources) that is loaded on demand.
- `kb/search.py` — `search(question, k=5)` returns passages with source title,
  URL, licence, publisher, country, chunk id and cosine score, sorted by score.
- `kb/chat.py`, `kb/api.py` — `POST /chat` accepts the existing web contract
  `{ lang, messages }` (or `{ question, k }`) and returns `{ reply, sources,
  citations, passages }`. Answers are extractive and numbered `[1]`, `[2]`
  against cited sources; with no relevant passage the reply is "I don't know"
  instead of invented advice; health questions defer to a local professional.
- `kb/evaluation/questions.json` — 10 representative farmer questions.
- `kb/evaluation/retrieval_results.md` — real top-5 retrieval results recorded
  with `python -m kb eval`.
- `tests/test_kb.py`, `tests/test_chat.py` — 23 unittest cases covering
  metadata/licences, digest availability, chunking, embeddings, ranking,
  validation, store roundtrip, evaluation evidence and grounded replies with a
  **mocked search function**.
- `README.md` — documented commands, data flow and response format;
  `.gitignore` for Python bytecode.

### Acceptance criteria

- [x] Sources and licences listed (`kb/sources.csv`, 25 rows)
- [x] Grounded replies cite sources (`kb/chat.py`, numbered citations + URLs)
- [x] Tests with mocked search pass

### Test log

```
$ python -m kb build
Indexed 75 chunks from 25 sources -> kb/index.json
$ python -m kb eval
Wrote kb/evaluation/retrieval_results.md
$ python -m unittest discover -s tests -v
Ran 23 tests in 0.3s
OK
```

Top-1 retrieval for all 10 recorded questions matched the expected topic
(maize planting, fall armyworm, cassava planting material, cassava post-harvest,
cowpea planting date, rice water management, sorghum/millet intercropping,
groundnut soils and rotation, water/hygiene, maize-legume intercropping).
