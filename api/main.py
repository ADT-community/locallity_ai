"""FastAPI entry point for the core chat API."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import llm as llm_module
from . import service

app = FastAPI(title="Locality AI Core API", version="1.0.0")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    lang: str = Field(..., min_length=1)
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=service.MAX_MESSAGES)


class ChatResponse(BaseModel):
    reply: str
    sources: list[str] = Field(default_factory=list)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        return service.chat(request.model_dump())
    except service.ChatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except llm_module.LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
