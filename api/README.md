# Locality AI Core API (v1)

A small FastAPI service that powers `POST /chat` for the web app, WhatsApp and API customers.

## Contract

```
POST /chat
{ "lang": "sw-KE", "messages": [{ "role": "user", "content": "..." }] }
-> { "reply": "...", "sources": [] }
```

`lang` is a locale such as `sw-KE` or `en-NG`; `messages` is a non-empty conversation
(roles: `user`, `assistant`, `system`). `sources` is always an empty list in v1 — the
knowledge base is a separate task. `GET /health` returns `{"status": "ok"}`.

## Run locally

```
python -m pip install -r api/requirements.txt
uvicorn api.main:app --reload
```

```
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"lang":"en-NG","messages":[{"role":"user","content":"How do I plant maize?"}]}'
```

Set `web/config.js` `apiUrl` to `http://127.0.0.1:8000/chat` to connect the web app.

## Configuration

The LLM key is read **only** from the environment — it is never stored in the repo.
Copy `api/.env.example` and fill in your own values in your shell or process manager:

| Variable | Meaning | Default |
|---|---|---|
| `LOCALLITY_LLM_API_KEY` | Key for the hosted OpenAI-compatible LLM (also accepts `OPENAI_API_KEY`) | none — `/chat` returns 503 for non-deferred questions |
| `LOCALLITY_LLM_BASE_URL` | API base URL | `https://api.openai.com/v1` |
| `LOCALLITY_LLM_MODEL` | Model name | `gpt-4o-mini` |

`api/llm.py` contains the single `call_llm()` function that performs the hosted call.
`api/prompt.py` builds the system prompt: short replies in the user's language,
`I don't know` when unsure, health questions referred to a local professional, and
refusals for emergencies or harm. `api/safety.py` adds a local deterministic safety net
so health, emergency and harm cases are deferred **before** any paid LLM call.

## Tests

No key, no network and no hosted account are needed: the LLM is mocked.

```
python -m unittest discover -s api/tests -v
python -m pytest api/tests -q
```

`api/tests/safety_cases.md` records 20 safety cases (10 to answer, 10 to defer). The
tests parse that table and check every case: answerable questions are passed to the
mocked LLM, deferred ones never reach it and return a short localised reply.

When FastAPI/httpx are installed, `api/tests/test_api.py` additionally exercises the
real HTTP endpoint via `TestClient`; it is skipped automatically otherwise.
