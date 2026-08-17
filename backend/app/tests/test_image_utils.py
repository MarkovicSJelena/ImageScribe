from io import BytesIO

import pytest
from PIL import Image
from fastapi import HTTPException

from app.core.config import settings
from app.utils.image import downscale_image, validate_image


def test_validate_image_rejects_empty_bytes():
    with pytest.raises(HTTPException) as exc:
        validate_image(b"", "image/png")
    assert exc.value.status_code == 422


def test_validate_image_rejects_oversized_bytes():
    payload = b"A" * ((settings.MAX_FILE_SIZE_MB + 1) * 1024 * 1024)
    with pytest.raises(HTTPException) as exc:
        validate_image(payload, "image/png")
    assert exc.value.status_code == 422


def test_validate_image_rejects_disallowed_mime_type():
    payload = b"not really an image"
    with pytest.raises(HTTPException) as exc:
        validate_image(payload, "text/plain")
    assert exc.value.status_code == 422


def test_validate_image_accepts_valid_jpeg_magic_bytes():
    buffer = BytesIO()
    Image.new("RGB", (16, 16), color="red").save(buffer, format="JPEG")
    payload = buffer.getvalue()
    assert validate_image(payload, "image/jpeg") == "image/jpeg"


def test_validate_image_accepts_octet_stream_for_valid_image_bytes():
    buffer = BytesIO()
    Image.new("RGB", (16, 16), color="green").save(buffer, format="PNG")
    payload = buffer.getvalue()
    assert validate_image(payload, "application/octet-stream") == "image/png"


def test_validate_image_rejects_pdf_magic_bytes_for_jpeg_mime():
    payload = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    with pytest.raises(HTTPException) as exc:
        validate_image(payload, "image/jpeg")
    assert exc.value.status_code == 422


def test_validate_image_returns_real_png_mime(sample_png_bytes):
    assert validate_image(sample_png_bytes, "image/png") == "image/png"


def test_validate_image_rejects_corrupted_png(sample_png_bytes):
    payload = sample_png_bytes[:-10] + b"\x00\x00\x00\x00"
    with pytest.raises(HTTPException) as exc:
        validate_image(payload, "image/png")
    assert exc.value.status_code == 422


def test_downscale_image_resizes_large_image():
    buffer = BytesIO()
    Image.new("RGB", (3000, 1200), color="green").save(buffer, format="PNG")
    content = buffer.getvalue()

    resized = downscale_image(content, settings.MAX_IMAGE_EDGE_PX)

    with Image.open(BytesIO(resized)) as img:
        max_edge = max(img.size)
        assert max_edge == settings.MAX_IMAGE_EDGE_PX


def test_downscale_image_returns_small_image_unchanged():
    buffer = BytesIO()
    Image.new("RGB", (32, 32), color="blue").save(buffer, format="PNG")
    content = buffer.getvalue()

    resized = downscale_image(content, settings.MAX_IMAGE_EDGE_PX)
    assert resized == content
