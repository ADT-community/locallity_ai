"""The single function that calls a hosted, OpenAI-compatible chat LLM."""

import json
import urllib.error
import urllib.request

from . import config

TIMEOUT = 20


class LLMError(RuntimeError):
    pass


def call_llm(messages, timeout=TIMEOUT):
    key = config.api_key()
    if not key:
        raise LLMError(
            "No LLM API key configured. Set LOCALLITY_LLM_API_KEY (or OPENAI_API_KEY)."
        )

    url = config.base_url() + "/chat/completions"
    body = json.dumps({
        "model": config.model(),
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 300,
    }).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise LLMError("LLM returned HTTP %s" % exc.code) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise LLMError("LLM request failed: %s" % exc) from exc

    try:
        return payload["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise LLMError("Unexpected LLM response shape") from exc
