"""Locality AI core API.

FastAPI app with a POST /chat endpoint that answers safely in the user's
language. The contract matches web/config.js:

    POST { lang, messages: [{ role, content }] } -> { reply, sources }

The brain is llm.chat(); no key is stored in this repo. With
LOCALITY_LLM_KEY unset the app runs in demo/mock mode so the safety tests
pass without a key.
"""

from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from . import llm  # package-relative import (api/ is a package)

app = FastAPI(title="Locality AI Core", version="0.1.0")


class Message(BaseModel):
    role: str = Field(..., description="one of user / assistant / system")
    content: str


class ChatRequest(BaseModel):
    lang: str = "en"
    messages: List[Message]


class ChatResponse(BaseModel):
    reply: str
    sources: Optional[List[str]] = []


@app.post("/chat", response_model=ChatResponse)
def post_chat(req: ChatRequest) -> ChatResponse:
    """Answer safely in the user's language."""
    if not req.messages:
        return ChatResponse(reply="Please ask a question.", sources=[])
    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    reply, sources = llm.chat(msgs, lang=req.lang)
    return ChatResponse(reply=reply, sources=sources)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": "demo" if not _has_key() else "live"}


def _has_key() -> bool:
    import os
    return bool(os.environ.get("LOCALITY_LLM_KEY", ""))
