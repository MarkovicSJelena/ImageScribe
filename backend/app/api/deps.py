from __future__ import annotations

from app.services.vision_service import describe_image


def get_vision_service():
    return describe_image
