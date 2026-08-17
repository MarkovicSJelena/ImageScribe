from __future__ import annotations

from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.api.deps import get_vision_service


def test_describe_route_enforces_rate_limit(client: TestClient):
    app.dependency_overrides[get_vision_service] = (
        lambda: lambda image_bytes, mime_type, style: "A test image."
    )

    try:
        buffer = BytesIO()
        Image.new("RGB", (32, 32), color="red").save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        responses = [
            client.post(
                "/api/describe",
                files={
                    "file": (
                        "test.png",
                        image_bytes,
                        "image/png",
                    )
                },
                data={"style": "Standard"},
            )
            for _ in range(25)
        ]

        assert any(response.status_code == 429 for response in responses)

    finally:
        app.dependency_overrides.clear()