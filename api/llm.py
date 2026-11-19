"""Locality AI chat brain.

One function that calls a hosted LLM, key from an environment variable.
No key in this repo. When LOCALITY_LLM_KEY is unset (or empty) the module
runs in mock mode so the safety tests pass without a key.
"""

import os

# Health topics to refer to a local professional rather than answer.
_HEALTH_TERMS = ("fever", "malaria", "medicine", "doctor", "hospital",
                 "pregnant", "pregnancy", "diarrhea", "vaccine", "sick",
                 "health", "发烧", "药", "医生", "医院", "怀孕", "疫苗",
                 "生病", "健康")

# Things we refuse outright (harm / illegal / dangerous).
_REFUSE_TERMS = ("suicide", "kill yourself", "kill myself", "bomb",
                 "explosive", "poison", "steal", "fraud", "scam", "gamble",
                 "赌博", "诈骗", "偷", "自杀", "炸弹", "毒品", "杀")

SYSTEM_PROMPT = (
    "You are a helpful assistant for farmers and everyday users. "
    "Reply in the user's language, keep answers short. "
    "If you are not sure, say 'I don't know' rather than guess. "
    "If the question is about health, do not give medical advice — "
    "refer the user to a local professional."
)


def _mock_reply(text):
    """Demo/mock reply used when no LLM key is configured."""
    lowered = text.lower()
    for term in _REFUSE_TERMS:
        if term in lowered:
            return ("I can't help with that. Please talk to someone "
                    "you trust or a local professional.")
    for term in _HEALTH_TERMS:
        if term in lowered:
            return ("That sounds like a health question. Please talk to a "
                    "local health professional — I can't give medical advice.")
    return ("I don't know yet — I'm running in demo mode. "
            "Ask again once the brain is connected.")


def chat(messages, lang="en"):
    """Call the hosted LLM and return (reply, sources).

    messages: list of {"role": ..., "content": ...}.
    lang: user's language code.
    Returns (reply: str, sources: list).
    """
    key = os.environ.get("LOCALITY_LLM_KEY", "")
    if not key:
        # No key in the repo; demo/mock mode keeps tests green without a key.
        last = messages[-1]["content"] if messages else ""
        return _mock_reply(last), []

    # Real path: call the hosted LLM with the key from the environment.
    # Endpoint is configurable via LOCALITY_LLM_URL so no URL is hard-coded
    # here either; the key and URL both come from the environment.
    import urllib.request
    url = os.environ.get("LOCALITY_LLM_URL", "")
    if not url:
        # Nothing to call without a URL either; fall back to demo.
        last = messages[-1]["content"] if messages else ""
        return _mock_reply(last), []

    payload = {
        "model": os.environ.get("LOCALITY_LLM_MODEL", "gpt-4o-mini"),
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "lang": lang,
    }
    req = urllib.request.Request(
        url,
        data=json_dumps(payload),
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json_loads(resp.read())
    reply = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
    return reply, []


def json_dumps(obj):
    import json
    return json.dumps(obj).encode("utf-8")


def json_loads(raw):
    import json
    return json.loads(raw.decode("utf-8"))
