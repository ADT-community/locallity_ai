"""Framework-agnostic POST /chat logic; shared by the FastAPI app and the tests."""

from . import llm as llm_module
from . import prompt, safety

MAX_MESSAGES = 50
MAX_CONTENT = 10000
ROLES = ("user", "assistant", "system")


class ChatError(ValueError):
    pass


def validate(payload):
    if not isinstance(payload, dict):
        raise ChatError("payload must be a JSON object")
    lang = payload.get("lang")
    if not isinstance(lang, str) or not lang.strip():
        raise ChatError("lang must be a non-empty string")
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ChatError("messages must be a non-empty list")
    if len(messages) > MAX_MESSAGES:
        raise ChatError("messages must contain at most %d items" % MAX_MESSAGES)
    cleaned = []
    for message in messages:
        if not isinstance(message, dict):
            raise ChatError("each message must be an object with role and content")
        role = message.get("role")
        content = message.get("content")
        if role not in ROLES:
            raise ChatError("message role must be user, assistant or system")
        if not isinstance(content, str) or not content.strip():
            raise ChatError("message content must be a non-empty string")
        if len(content) > MAX_CONTENT:
            raise ChatError("message content is too long")
        cleaned.append({"role": role, "content": content})
    return lang.strip(), cleaned


def last_user_text(messages):
    for message in reversed(messages):
        if message["role"] == "user":
            return message["content"]
    return ""


def chat(payload, llm=None):
    lang, messages = validate(payload)
    question = last_user_text(messages)
    category = safety.check(question)
    if category:
        return {"reply": safety.deferral(lang, category), "sources": []}
    caller = llm or llm_module.call_llm
    reply = caller(prompt.build_messages(lang, messages))
    if not isinstance(reply, str) or not reply.strip():
        raise ChatError("LLM returned an empty reply")
    return {"reply": reply.strip(), "sources": []}
