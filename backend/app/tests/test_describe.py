from app.main import app
from app.schemas.description import DescriptionStyle
from app.services.prompts import STYLE_PROMPTS
from app.services.vision_service import _sanitize_description, _strip_think_blocks


def test_short_style_prompt_requires_single_sentence_and_no_analysis():
    prompt = STYLE_PROMPTS[DescriptionStyle.Short].lower()

    assert "exactly one sentence" in prompt or "one sentence" in prompt
    assert "analysis" in prompt or "reasoning" in prompt
    assert "no <think>" in prompt or "no analysis" in prompt or "no preamble" in prompt


def test_strip_think_blocks_removes_reasoning_tags():
    raw = "<think>Reasoning text here</think>\nThis is the final sentence."

    assert _strip_think_blocks(raw) == "This is the final sentence."


def test_sanitize_short_description_keeps_only_first_sentence():
    raw = "<think>Reasoning</think> This is the final sentence. Second sentence should be dropped."

    assert _sanitize_description(raw, DescriptionStyle.Short) == "This is the final sentence."


def test_describe_route_success(client, sample_png_bytes):
    def fake_service(image_bytes: bytes, mime_type: str, style):
        assert image_bytes == sample_png_bytes
        assert mime_type == "image/png"
        return "A generated description"

    from app.api.deps import get_vision_service

    app.dependency_overrides[get_vision_service] = lambda: fake_service
    try:
        response = client.post(
            "/api/describe",
            files={"file": ("sample.png", sample_png_bytes, "image/png")},
            data={"style": "Standard"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "style": "Standard",
        "description": "A generated description",
    }


def test_describe_route_rejects_invalid_file(client):
    response = client.post(
        "/api/describe",
        files={"file": ("fake.pdf", b"%PDF-1.4", "application/pdf")},
        data={"style": "Standard"},
    )

    assert response.status_code == 422
    assert "image" in response.text.lower()


def test_describe_route_maps_provider_error_to_502(client, sample_png_bytes):
    def failing_service(image_bytes: bytes, mime_type: str, style):
        raise RuntimeError("provider exploded")

    from app.api.deps import get_vision_service

    app.dependency_overrides[get_vision_service] = lambda: failing_service
    try:
        response = client.post(
            "/api/describe",
            files={"file": ("sample.png", sample_png_bytes, "image/png")},
            data={"style": "Standard"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert "unavailable" in response.json()["detail"].lower()
