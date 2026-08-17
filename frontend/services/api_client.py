from __future__ import annotations

import mimetypes

import httpx

from core.config import API_BASE_URL, REQUEST_TIMEOUT_SECONDS


def fetch_styles() -> list[str]:
    response = httpx.get(f"{API_BASE_URL}/api/styles", timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise ValueError("Unexpected response from /api/styles")
    return [str(item) for item in data]


def describe_image(file_bytes: bytes, file_name: str, style: str) -> str:
    guessed_mime = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
    files = {"file": (file_name, file_bytes, guessed_mime)}
    data = {"style": style}

    response = httpx.post(
        f"{API_BASE_URL}/api/describe",
        files=files,
        data=data,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    return str(payload.get("description", ""))
