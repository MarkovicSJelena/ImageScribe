from __future__ import annotations

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (32, 32), color="blue").save(buffer, format="PNG")
    return buffer.getvalue()