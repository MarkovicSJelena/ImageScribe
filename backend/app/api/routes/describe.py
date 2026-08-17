from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.api.deps import get_vision_service
from app.main import limiter
from app.schemas.description import DescriptionResponse, DescriptionStyle
from app.utils.image import validate_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["describe"])


@router.post("/describe", response_model=DescriptionResponse)
@limiter.limit("20/minute")
def describe_image(
    request: Request,
    file: Annotated[UploadFile, File(...)],
    style: Annotated[DescriptionStyle, Form()] = DescriptionStyle.Standard,
    vision_service=Depends(get_vision_service),
):
    """Generate a description for an uploaded image."""
    image_bytes = file.file.read()
    mime_type = file.content_type or "application/octet-stream"

    valid_mime = validate_image(image_bytes, mime_type)

    try:
        description = vision_service(image_bytes, valid_mime, style)
    except Exception:
        logger.exception("Image description provider failed.")
        raise HTTPException(
            status_code=502,
            detail="Image description service is unavailable right now. Please try again later.",
        ) from None

    return DescriptionResponse(style=style, description=description)
