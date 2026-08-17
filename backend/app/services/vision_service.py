from __future__ import annotations

import base64
import logging
import re
from io import BytesIO
from typing import Any

from PIL import Image

from app.core.config import settings
from app.schemas.description import DescriptionStyle
from app.services.prompts import STYLE_PROMPTS, STYLE_TEMPERATURE, SYSTEM_PROMPT
from app.utils.image import downscale_image, validate_image

logger = logging.getLogger(__name__)


def _strip_think_blocks(text: str) -> str:
    cleaned = re.sub(r"(?is)<think>.*?(?:</think>|$)", "", text)
    cleaned = re.sub(r"(?is)\s+", " ", cleaned).strip()
    return cleaned


def _sanitize_description(text: str, style: DescriptionStyle) -> str:
    cleaned = _strip_think_blocks(text)

    if not cleaned:
        return ""

    if style == DescriptionStyle.Short:
        parts = re.split(r"(?<=[.!?])\s+", cleaned)
        final_parts = [part.strip() for part in parts if part.strip()]
        if final_parts:
            return final_parts[0]

    return cleaned


def _mock_describe_image(style: DescriptionStyle) -> str:
    return f"Mock description for {style.value} style: a simple placeholder result generated locally without an API call."


def describe_image(image_bytes: bytes, mime_type: str, style: DescriptionStyle | str) -> str:
    """Describe an image using the configured Groq backend.

    If no Groq key is configured, we intentionally fall back to a local mock
    response so the app remains usable in development and tests without API spend.
    """
    validated_mime = validate_image(image_bytes, mime_type)
    normalized_style = style if isinstance(style, DescriptionStyle) else DescriptionStyle(style)

    groq_key = __import__("os").getenv("GROQ_API_KEY") or settings.GROQ_API_KEY
    if not groq_key:
        logger.info("Using mock vision fallback because GROQ_API_KEY is not configured.")
        return _mock_describe_image(normalized_style)

    processed = downscale_image(image_bytes, settings.MAX_IMAGE_EDGE_PX)

    if not processed:
        processed = image_bytes

    encoded = base64.b64encode(processed).decode("utf-8")
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Style: {normalized_style.value}\n"
        f"Instruction: {STYLE_PROMPTS[normalized_style]}\n"
        f"Return a description in the requested style."
    )

    logger.info(
        "Calling vision provider",
        extra={
            "model": settings.GROQ_MODEL,
            "mime_type": validated_mime,
            "style": normalized_style.value,
            "bytes_in": len(image_bytes),
            "bytes_out": len(processed),
            "temperature": STYLE_TEMPERATURE[normalized_style],
        },
    )

    try:
        from app.services.groq_client import get_client

        client = get_client()
        response = client.invoke(
            [
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{validated_mime};base64,{encoded}"}},
                ]}
            ]
        )

        text = getattr(response, "content", str(response))
        if isinstance(text, list):
            text = "".join(str(part.get("text", "")) for part in text if isinstance(part, dict))
        return _sanitize_description(str(text), normalized_style)
    except Exception as exc:
        logger.exception("Provider failure while describing image.")
        raise RuntimeError("Image description provider failed.") from exc
