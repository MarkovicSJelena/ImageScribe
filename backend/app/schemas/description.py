from enum import Enum

from pydantic import BaseModel


class DescriptionStyle(str, Enum):
    Standard = "Standard"
    Short = "Short"
    Detailed = "Detailed"
    SEO_ECOMMERCE = "SEO / E-commerce"
    Creative = "Creative"


class DescriptionResponse(BaseModel):
    style: DescriptionStyle
    description: str
