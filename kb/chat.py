"""Grounded answers: every factual passage is cited with a trusted source link."""

import re

from . import search as search_module

HEALTH_TERMS = (
    "fever", "malaria", "medicine", "doctor", "hospital", "pregnant", "pregnancy",
    "diarrhea", "diarrhoea", "vaccine", "sick", "health", "cholera", "headache",
)

DEFER_REPLY = (
    "That sounds like a health question. I can only share basic, trusted guidance "
    "about water and hygiene, not medical advice. Please talk to a local health "
    "professional or clinic for advice about your situation."
)

UNKNOWN_REPLY = (
    "I don't know from my trusted farming sources. Try rephrasing the question, "
    "or ask your local extension service for advice specific to your area."
)

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _excerpt(text, limit=420):
    if len(text) <= limit:
        return text
    cut = text[:limit]
    sentences = _SENTENCE_RE.split(cut)
    if len(sentences) > 1:
        cut = " ".join(sentences[:-1])
    return cut.rstrip(",;: ") + "…"


def _is_health(question):
    lowered = question.lower()
    return any(term in lowered for term in HEALTH_TERMS)


def answer(question, k=5, search_fn=None, min_score=0.02):
    """Build an extractive, cited reply from retrieval results.

    ``search_fn`` is injectable so tests can supply mocked retrieval results.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string")
    finder = search_fn or search_module.search
    results = finder(question, k=k)
    passages = [result for result in results if result.get("score", 0) >= min_score]
    sources = []
    citation_numbers = {}
    for result in passages:
        source_id = result.get("source_id", result.get("url"))
        if source_id in citation_numbers:
            continue
        citation_numbers[source_id] = len(citation_numbers) + 1
        sources.append({
            "number": citation_numbers[source_id],
            "title": result.get("title", result.get("source", "")),
            "url": result.get("url", ""),
            "publisher": result.get("publisher", ""),
            "license": result.get("license", ""),
            "topic": result.get("topic", ""),
            "country": result.get("country", ""),
        })
    if not passages:
        return {"reply": UNKNOWN_REPLY, "sources": [], "passages": []}

    if _is_health(question):
        reply = DEFER_REPLY
        if sources:
            reply += " Source: " + ", ".join(
                "%s [%d]" % (source["title"], source["number"]) for source in sources
            )
        return {"reply": reply, "sources": sources, "passages": passages}

    parts = []
    for position, result in enumerate(passages[:2]):
        source_id = result.get("source_id", result.get("url"))
        marker = "[%d]" % citation_numbers[source_id]
        parts.append("%s %s" % (_excerpt(result["passage"]), marker))
    reply = " ".join(parts)
    reply += "\n\nSources: " + "; ".join(
        "[%d] %s — %s (%s)" % (source["number"], source["title"],
                               source["url"], source["license"])
        for source in sources
    )
    return {"reply": reply, "sources": sources, "passages": passages}


def handle_chat(payload, search_fn=None):
    """Framework-agnostic ``POST /chat`` handler matching web/config.js."""
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    messages = payload.get("messages") or []
    if messages:
        question = messages[-1].get("content", "")
    else:
        question = payload.get("question", payload.get("message", ""))
    k = payload.get("k", 5)
    if not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    limit = min(k, 10)
    result = answer(question, k=limit, search_fn=search_fn)
    return {
        "reply": result["reply"],
        "sources": [source["url"] for source in result["sources"]],
        "citations": result["sources"],
        "passages": result["passages"],
    }
