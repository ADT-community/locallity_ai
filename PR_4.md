Closes #4

## What this adds

A self-contained core API in `api/` implementing the `POST /chat` contract used by `web/config.js`:

- `POST /chat` takes `{ lang, messages: [{ role, content }] }` and returns `{ reply, sources }`. `GET /health` is included for checks.
- `api/main.py` — FastAPI app with Pydantic request/response models and clear HTTP errors (400 invalid input, 503 when no LLM key is configured).
- `api/llm.py` — one `call_llm()` function that calls a hosted OpenAI-compatible chat endpoint using only the standard library. The key comes exclusively from `LOCALLITY_LLM_API_KEY` / `OPENAI_API_KEY`; there is no key in the repository.
- `api/prompt.py` — system prompt: reply in the user's language, keep it short, say "I don't know" when unsure, refer health questions to a local health professional, refuse emergencies and harmful requests.
- `api/safety.py` — deterministic local safety net that defers health, emergency and harm cases **before** any LLM call, with short replies in 12 languages. `sources` is an empty list because the knowledge base is out of scope.
- `api/tests/safety_cases.md` — 20 recorded cases (10 answer, 10 defer), parsed by the tests so documentation and behaviour cannot drift apart.
- Tests mock the LLM: 18 tests plus 26 subtests check the contract, prompt rules, validation, locale handling and every safety case. They pass with no key and no network.
- `api/README.md`, `api/.env.example`, `api/requirements.txt`, and short root-README links give run/config instructions. A root `.gitignore` keeps `.env` and bytecode out of the repo.

`web/` and the knowledge base were not modified.

## Verification

```
python -m pip install -r api/requirements.txt
python -m unittest discover -s api/tests -v
Ran 18 tests ... OK
python -m pytest api/tests -q
18 passed, 1 warning, 26 subtests passed in 0.74s
python -m py_compile api/*.py api/tests/*.py   (no errors)
```

The single warning is Starlette's deprecation notice about using `httpx` with `TestClient`; all endpoint tests pass.
