from fastapi import APIRouter

from app.schemas.description import DescriptionStyle

router = APIRouter(prefix="/api", tags=["styles"])


@router.get("/styles")
def get_styles() -> list[str]:
    return [style.value for style in DescriptionStyle]
