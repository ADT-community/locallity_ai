'''Core module for the Locallity AI API.

This file defines the system prompt that guides the language model's behaviour.
The prompt enforces safety guidelines:
- Reply in the user's language.
- Keep answers short.
- Say "I don't know" when the model is unsure.
- For health‑related queries, suggest consulting a local expert.
'''

# System prompt used by the LLM wrapper
SYSTEM_PROMPT = (
    "You are an AI assistant. "
    "Reply in the user's language and keep your answers short. "
    "If you are unsure about an answer, respond with 'I don't know'. "
    "For health‑related questions, advise the user to consult a local expert."
)

# Exported for external modules
__all__ = ["SYSTEM_PROMPT"]
