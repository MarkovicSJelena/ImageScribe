from __future__ import annotations

from io import BytesIO

from fastapi import HTTPException
from PIL import Image

from app.core.config import settings

_ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

_SIGNATURES: dict[str, bytes] = {
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/webp": b"RIFF",
}


def _detect_by_magic_bytes(content: bytes) -> str | None:
    if content.startswith(_SIGNATURES["image/jpeg"]):
        return "image/jpeg"
    if content.startswith(_SIGNATURES["image/png"]):
        return "image/png"
    if content.startswith(_SIGNATURES["image/webp"]) and content[8:12] == b"WEBP":
        return "image/webp"
    return None


def downscale_image(content: bytes, max_edge: int) -> bytes:
    """Resize images proportionally if their longest edge exceeds the configured limit."""
    with Image.open(BytesIO(content)) as img:
        width, height = img.size
        longest_edge = max(width, height)

        if longest_edge <= max_edge:
            return content

        scale = max_edge / longest_edge
        new_width = max(1, int(round(width * scale)))
        new_height = max(1, int(round(height * scale)))

        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        output = BytesIO()
        resized.save(output, format=img.format or "PNG")
        return output.getvalue()


def validate_image(content: bytes, declared_mime: str | None) -> str:
    """Validate uploaded image payloads at the boundary before any model call."""
    if not content:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=422,
            detail=f"Uploaded file exceeds the {settings.MAX_FILE_SIZE_MB} MB limit.",
        )

    detected_mime = _detect_by_magic_bytes(content)
    if detected_mime is None:
        raise HTTPException(
            status_code=422,
            detail="Unsupported file type. Please upload a JPEG, PNG, or WEBP image.",
        )

    if declared_mime is not None and declared_mime not in _ALLOWED_MIME_TYPES and declared_mime != "application/octet-stream":
        raise HTTPException(
            status_code=422,
            detail="Unsupported file type. Please upload a JPEG, PNG, or WEBP image.",
        )

    if declared_mime is not None and declared_mime not in {"application/octet-stream", detected_mime}:
        raise HTTPException(
            status_code=422,
            detail="File content does not match the declared image type.",
        )

    try:
        with Image.open(BytesIO(content)) as img:
            img.verify()
            real_mime = img.get_format_mimetype() or detected_mime
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Corrupted or invalid image file.") from exc

    if real_mime not in _ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=422,
            detail="Unsupported file type. Please upload a JPEG, PNG, or WEBP image.",
        )

    if declared_mime is not None and declared_mime not in {"application/octet-stream", real_mime}:
        raise HTTPException(
            status_code=422,
            detail="Image format does not match the declared MIME type.",
        )

    return real_mime
