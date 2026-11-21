"""Environment-based configuration. Secrets are never stored in this repository."""

import os

API_KEY_VARS = ("LOCALLITY_LLM_API_KEY", "OPENAI_API_KEY")
BASE_URL_VAR = "LOCALLITY_LLM_BASE_URL"
MODEL_VAR = "LOCALLITY_LLM_MODEL"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


def api_key():
    for name in API_KEY_VARS:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def base_url():
    value = os.environ.get(BASE_URL_VAR, "").strip().rstrip("/")
    return value or DEFAULT_BASE_URL


def model():
    return os.environ.get(MODEL_VAR, "").strip() or DEFAULT_MODEL
