"""Pydantic schemas for concept node explanations."""

from datetime import datetime
from typing import Any
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator


class NodeExplanationOutput(BaseModel):
    """Structured LLM output schema for node knowledge explanations."""

    overview: str = Field(
        min_length=1,
        max_length=5000,
        description="High-level overview and intuitive explanation",
    )
    detailed_explanation: str = Field(
        min_length=1,
        max_length=20000,
        description="Comprehensive deep-dive explanation of the concept",
    )
    how_it_works: list[str] = Field(
        default_factory=list,
        description="Step-by-step breakdown of mechanics or processes",
    )
    key_concepts: list[str] = Field(
        default_factory=list,
        description="Core terminology and fundamental principles",
    )
    examples: list[str] = Field(
        default_factory=list,
        description="Real-world practical examples",
    )
    applications: list[str] = Field(
        default_factory=list,
        description="Industry use-cases and scenarios",
    )
    related_concepts: list[str] = Field(
        default_factory=list,
        description="Adjacent concepts and cross-domain connections",
    )

    @field_validator(
        "how_it_works",
        "key_concepts",
        "examples",
        "applications",
        "related_concepts",
        mode="before",
    )
    @classmethod
    def coerce_to_string_list(cls, v: Any) -> list[str]:
        """Ensure all list fields are robustly coerced into lists of clean strings."""
        if not v:
            return []
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            result = []
            for item in v:
                if isinstance(item, dict):
                    desc = item.get("description") or item.get("detail") or item.get("text") or item.get("explanation")
                    title = item.get("title") or item.get("concept") or item.get("name") or item.get("step")
                    if title and desc:
                        result.append(f"{title}: {desc}")
                    elif desc:
                        result.append(str(desc))
                    elif title:
                        result.append(str(title))
                    else:
                        result.append(", ".join(f"{k}: {val}" for k, val in item.items()))
                else:
                    result.append(str(item))
            return result
        return [str(v)]


class NodeExplanationRead(NodeExplanationOutput):
    """Schema for returning persisted node explanations."""

    id: uuid.UUID
    node_id: uuid.UUID
    level: str
    model_name: str
    version: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
