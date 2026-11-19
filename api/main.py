import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Locality AI Core API")

# Supported languages (ISO 639-1 or BCP 47)
SUPPORTED_LANGUAGES = {
    "sw-KE", "en-NG", "zu-ZA", "xh-ZA", "af-ZA", "am-ET", "yo-NG", "ha-NG", "ig-NG", "rw-RW", "so-SO", "fr-SN"
}

# Fallback to base language codes if specific regional codes are not provided
BASE_LANGUAGES = {"sw", "en", "zu", "xh", "af", "am", "yo", "ha", "ig", "rw", "so", "fr"}

class ChatRequest(BaseModel):
    lang: str
    messages: List[dict]

class ChatResponse(BaseModel):
    reply: str

def is_supported_language(lang: str) -> bool:
    if lang in SUPPORTED_LANGUAGES:
        return True
    # Check base language (e.g., 'sw' from 'sw-KE')
    base = lang.split('-')[0].lower()
    return base in BASE_LANGUAGES

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not is_supported_language(request.lang):
        raise HTTPException(status_code=400, detail=f"Unsupported language: {request.lang}")
    
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")

    llm_api_url = os.getenv("LLM_API_URL")
    llm_api_key = os.getenv("LLM_API_KEY")
    
    if not llm_api_url:
        raise HTTPException(status_code=500, detail="LLM_API_URL is not configured")

    # Construct the prompt to enforce language
    system_prompt = f"You are a helpful assistant. You MUST respond ONLY in {request.lang}. Do not use any other language."
    
    # Prepare messages for the LLM
    llm_messages = [{"role": "system", "content": system_prompt}]
    for msg in request.messages:
        if "role" in msg and "content" in msg:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {llm_api_key}"} if llm_api_key else {}
            response = await client.post(llm_api_url, json={"messages": llm_messages}, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Assuming OpenAI-like response format
            if "choices" in data and len(data["choices"]) > 0:
                reply = data["choices"][0]["message"]["content"]
                return ChatResponse(reply=reply)
            else:
                raise HTTPException(status_code=502, detail="Unexpected LLM response format")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error communicating with LLM: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok"}
