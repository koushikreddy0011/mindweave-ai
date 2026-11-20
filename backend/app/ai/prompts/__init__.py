"""AI prompts package."""

from app.ai.prompts.explanation_prompts import (
    NODE_EXPLANATION_SYSTEM_PROMPT,
    build_explanation_prompt,
)
from app.ai.prompts.mindmap_prompts import (
    MINDMAP_SYSTEM_PROMPT,
    build_topic_prompt,
)

__all__ = [
    "MINDMAP_SYSTEM_PROMPT",
    "build_topic_prompt",
    "NODE_EXPLANATION_SYSTEM_PROMPT",
    "build_explanation_prompt",
]
