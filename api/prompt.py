"""The system prompt that defines safe behaviour for every chat reply."""

LANGUAGE_NAMES = {
    "en": "English",
    "sw": "Kiswahili",
    "zu": "isiZulu",
    "xh": "isiXhosa",
    "af": "Afrikaans",
    "am": "Amharic",
    "yo": "Yoruba",
    "ha": "Hausa",
    "ig": "Igbo",
    "rw": "Kinyarwanda",
    "so": "Somali",
    "fr": "French",
}

SYSTEM_RULES = (
    "You are Locality AI, a helpful assistant for everyday and farming questions. "
    "Always reply in {language}, the user's language, even if the question uses other languages. "
    "Keep replies short: one to three sentences. "
    "If you are unsure or do not know the answer, say \"I don't know\" in the user's language "
    "instead of guessing or inventing facts. "
    "Never diagnose, prescribe medicine or give medical instructions: for any health question, "
    "tell the user to talk to a local health professional or clinic. "
    "For emergencies or requests to do harm, refuse and tell the user to contact local emergency services. "
    "Be clear, kind and practical."
)


def language_name(lang):
    if not isinstance(lang, str):
        return LANGUAGE_NAMES["en"]
    base = lang.strip().lower().replace("_", "-").split("-")[0]
    return LANGUAGE_NAMES.get(base, LANGUAGE_NAMES.get(base[:2], LANGUAGE_NAMES["en"]))


def system_prompt(lang):
    return SYSTEM_RULES.format(language=language_name(lang))


def build_messages(lang, messages):
    return [{"role": "system", "content": system_prompt(lang)}] + [
        {"role": message["role"], "content": message["content"]} for message in messages
    ]
