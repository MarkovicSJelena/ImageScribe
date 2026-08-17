from io import BytesIO

from PIL import Image

from app.core.config import settings
from app.schemas.description import DescriptionStyle
from app.services.vision_service import describe_image


def test_describe_image_returns_mock_result_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(settings, "GROQ_API_KEY", None)

    buffer = BytesIO()
    Image.new("RGB", (32, 32), color="purple").save(buffer, format="PNG")

    result = describe_image(buffer.getvalue(), "image/png", DescriptionStyle.Standard)

    assert "Mock" in result
    assert "Standard" in result


def test_describe_image_downscales_large_image_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(settings, "GROQ_API_KEY", None)

    buffer = BytesIO()
    Image.new("RGB", (3000, 1200), color="orange").save(buffer, format="PNG")

    result = describe_image(buffer.getvalue(), "image/png", DescriptionStyle.Creative)

    assert "Mock" in result
    assert "Creative" in result
