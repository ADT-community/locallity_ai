"""Locality AI knowledge base: trusted sources, grounded retrieval and answers."""

from .search import KnowledgeBase, get_kb, set_kb
from .chat import answer, handle_chat

__all__ = ["KnowledgeBase", "get_kb", "set_kb", "answer", "handle_chat"]
