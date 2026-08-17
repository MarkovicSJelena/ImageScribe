from __future__ import annotations

from app.schemas.description import DescriptionStyle

SYSTEM_PROMPT = """You are an expert image analyst and caption writer.
Describe what is visible in the image accurately, clearly, and in the requested style.
Do not invent details that are not visible.
"""

STYLE_PROMPTS = {
    DescriptionStyle.Standard: "Describe the image in a balanced, neutral, 3-4 sentence summary.",
    DescriptionStyle.Short: "Return exactly one sentence only. Output the final answer only, with no analysis, no reasoning, no <think> tags, no preamble, and no extra text.",
    DescriptionStyle.Detailed: "Provide a detailed analysis of composition, colors, lighting, objects, and context in up to 250 words.",
    DescriptionStyle.SEO_ECOMMERCE: "Write a product-focused description with a short title, 2-3 selling sentences, and 5 keywords.",
    DescriptionStyle.Creative: "Write a vivid, imaginative marketing-style description in up to 120 words.",
}

STYLE_TEMPERATURE = {
    DescriptionStyle.Standard: 0.4,
    DescriptionStyle.Short: 0.2,
    DescriptionStyle.Detailed: 0.3,
    DescriptionStyle.SEO_ECOMMERCE: 0.5,
    DescriptionStyle.Creative: 0.9,
}


def validate_prompt_catalog() -> None:
    missing = [style for style in DescriptionStyle if style not in STYLE_PROMPTS or style not in STYLE_TEMPERATURE]
    if missing:
        raise ValueError(f"Missing prompt configuration for: {[s.value for s in missing]}")


validate_prompt_catalog()
