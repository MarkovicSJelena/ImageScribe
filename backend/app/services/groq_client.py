from __future__ import annotations

import os
from typing import Any

from langchain_groq import ChatGroq

from app.core.config import settings

_client: Any | None = None
_client_key: tuple[str, str] | None = None


def get_client() -> Any:
    global _client, _client_key

    api_key = os.getenv("GROQ_API_KEY") or settings.GROQ_API_KEY
    model = os.getenv("GROQ_MODEL") or settings.GROQ_MODEL
    cache_key = (api_key or "", model)

    if _client is not None and _client_key == cache_key:
        return _client

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured. Set it in the environment or .env file before creating the Groq client.")

    _client = ChatGroq(
        model=model,
        api_key=api_key,
        temperature=0.2,
    )
    _client_key = cache_key
    return _client
