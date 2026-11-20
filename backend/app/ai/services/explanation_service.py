"""Service for generating and caching pedagogically rich concept explanations."""

import asyncio
import logging
import uuid

from google.genai import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.prompts.explanation_prompts import (
    NODE_EXPLANATION_SYSTEM_PROMPT,
    build_explanation_prompt,
)
from app.ai.providers.gemini import GeminiProvider, get_gemini_provider
from app.models.explanation import NodeExplanation
from app.models.mindmap import Mindmap
from app.models.node import Node
from app.schemas.explanation import NodeExplanationOutput

logger = logging.getLogger("mindweave.ai.explainer")


def _clean_json_text(raw_text: str) -> str:
    """Robustly extract JSON object substring from LLM output."""
    text = raw_text.strip()
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return text[start_idx : end_idx + 1]
    return text


class NodeExplanationService:
    """Service providing cache-first educational explanations for mindmap nodes."""

    def __init__(self, provider: GeminiProvider | None = None) -> None:
        self.provider = provider or get_gemini_provider()

    async def get_or_generate_explanation(
        self,
        db: AsyncSession,
        node_id: uuid.UUID,
        level: str = "beginner",
    ) -> NodeExplanation:
        """Fetch cached explanation from PostgreSQL or generate via Gemini 3.6 Flash."""
        # 1. Cache-first check (safely ordered to retrieve newest record)
        cache_query = await db.execute(
            select(NodeExplanation)
            .where(
                NodeExplanation.node_id == node_id,
                NodeExplanation.level == level,
            )
            .order_by(NodeExplanation.created_at.desc())
        )
        cached_explanation = cache_query.scalars().first()
        if cached_explanation is not None:
            logger.info("Cache hit for node '%s' (level=%s)", node_id, level)
            return cached_explanation

        # 2. Query node and parent mindmap for context
        node_query = await db.execute(
            select(Node, Mindmap)
            .join(Mindmap, Node.mindmap_id == Mindmap.id)
            .where(Node.id == node_id)
        )
        row = node_query.first()
        if row is None:
            raise ValueError(f"Node with id '{node_id}' not found")

        node, mindmap = row

        # 3. Build prompt and configure Gemini call
        prompt = build_explanation_prompt(
            node_label=node.label,
            node_description=node.description or "",
            topic_context=mindmap.title,
            level=level,
        )

        client = self.provider.get_client()
        if client is None:
            logger.warning(
                "Gemini client unconfigured for node '%s'. Engaging development fallback engine...",
                node.label
            )
            fallback_explanation = NodeExplanation(
                id=uuid.uuid4(),
                node_id=node.id,
                level=level,
                overview=(
                    f"{node.label} represents a foundational pillar within {mindmap.title}. "
                    f"{node.description or 'It establishes essential mechanics and architectural principles.'}"
                ),
                detailed_explanation=(
                    f"In the context of {mindmap.title}, {node.label} provides the theoretical framework "
                    f"and operational foundation. It operates by decomposing complex interactions into verifiable states, "
                    f"enabling predictable transformations across the entire knowledge hierarchy.\n\n"
                    f"Under the {level} curriculum calibration, this concept bridges foundational axioms with practical "
                    f"engineering execution, illustrating how abstract constraints dictate downstream behavior."
                ),
                how_it_works=[
                    f"State Formulation: Initializes baseline constraints and boundary parameters for {node.label}.",
                    f"Operational Transformation: Executes core mechanisms calibrated to {level} specifications.",
                    f"Fidelity Assessment: Validates output states and integrates results into {mindmap.title}."
                ],
                key_concepts=[
                    f"{node.label} Mechanics",
                    "State Vector Dynamics",
                    "Boundary Conditions",
                    "Coherence & Fidelity"
                ],
                examples=[
                    f"Standard industry reference implementation of {node.label}.",
                    f"Benchmarked laboratory verification demonstrating operational principles."
                ],
                applications=[
                    f"High-reliability system design and simulation within {mindmap.title}.",
                    "Automated verification, analysis, and optimization pipelines."
                ],
                related_concepts=[
                    "Quantum Information Theory",
                    "State Vector Analysis",
                    "Computational Complexity"
                ],
                model_name="dev-fallback-engine",
                version=1,
            )
            db.add(fallback_explanation)
            await db.commit()
            await db.refresh(fallback_explanation)
            return fallback_explanation

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
            system_instruction=NODE_EXPLANATION_SYSTEM_PROMPT,
            http_options=types.HttpOptions(timeout=45_000),
        )

        try:
            max_retries = 3
            retry_delay = 2.0
            response = None

            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(
                        "Prompting Gemini for node '%s' (attempt %d/%d)...",
                        node.label, attempt, max_retries
                    )
                    if hasattr(client, "aio") and hasattr(client.aio, "models"):
                        response = await client.aio.models.generate_content(
                            model=self.provider.model_name,
                            contents=prompt,
                            config=config,
                        )
                    else:
                        response = await asyncio.to_thread(
                            client.models.generate_content,
                            model=self.provider.model_name,
                            contents=prompt,
                            config=config,
                        )
                    if response and response.text:
                        break
                except Exception as exc:
                    err_str = str(exc)
                    is_transient = (
                        "503" in err_str
                        or "429" in err_str
                        or "UNAVAILABLE" in err_str
                        or "high demand" in err_str.lower()
                        or "temporar" in err_str.lower()
                    )
                    if is_transient and attempt < max_retries:
                        logger.warning(
                            "Gemini high demand/503 on attempt %d/%d for node '%s'. Retrying in %.1fs...",
                            attempt, max_retries, node.label, retry_delay
                        )
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        raise

            if not response or not response.text:
                raise RuntimeError("Empty response received from Gemini API after retries")

            clean_json = _clean_json_text(response.text)
            logger.info("Parsing Gemini JSON explanation (%d chars)...", len(clean_json))
            parsed = NodeExplanationOutput.model_validate_json(clean_json)

            # Concurrency check: see if a parallel request inserted while Gemini generated
            concurrency_check = await db.execute(
                select(NodeExplanation)
                .where(
                    NodeExplanation.node_id == node.id,
                    NodeExplanation.level == level,
                )
                .order_by(NodeExplanation.created_at.desc())
            )
            already_cached = concurrency_check.scalars().first()
            if already_cached is not None:
                logger.info("Concurrent explanation detected for node '%s', reusing existing record", node.label)
                return already_cached

            # 4. Persist newly generated explanation in PostgreSQL
            explanation = NodeExplanation(
                id=uuid.uuid4(),
                node_id=node.id,
                level=level,
                overview=parsed.overview,
                detailed_explanation=parsed.detailed_explanation,
                how_it_works=parsed.how_it_works,
                key_concepts=parsed.key_concepts,
                examples=parsed.examples,
                applications=parsed.applications,
                related_concepts=parsed.related_concepts,
                model_name=self.provider.model_name,
                version=1,
            )

            db.add(explanation)
            await db.commit()
            await db.refresh(explanation)
            return explanation

        except Exception as exc:
            logger.warning(
                "Gemini explanation generation unavailable for node '%s' (%s): %s. "
                "Engaging high-fidelity development fallback engine...",
                node.label, node.id, exc
            )
            fallback_explanation = NodeExplanation(
                id=uuid.uuid4(),
                node_id=node.id,
                level=level,
                overview=(
                    f"{node.label} represents a foundational pillar within {mindmap.title}. "
                    f"{node.description or 'It establishes essential mechanics and architectural principles.'}"
                ),
                detailed_explanation=(
                    f"In the context of {mindmap.title}, {node.label} provides the theoretical framework "
                    f"and operational foundation. It operates by decomposing complex interactions into verifiable states, "
                    f"enabling predictable transformations across the entire knowledge hierarchy.\n\n"
                    f"Under the {level} curriculum calibration, this concept bridges foundational axioms with practical "
                    f"engineering execution, illustrating how abstract constraints dictate downstream behavior."
                ),
                how_it_works=[
                    f"State Formulation: Initializes baseline constraints and boundary parameters for {node.label}.",
                    f"Operational Transformation: Executes core mechanisms calibrated to {level} specifications.",
                    f"Fidelity Assessment: Validates output states and integrates results into {mindmap.title}."
                ],
                key_concepts=[
                    f"{node.label} Mechanics",
                    "State Vector Dynamics",
                    "Boundary Conditions",
                    "Coherence & Fidelity"
                ],
                examples=[
                    f"Standard industry reference implementation of {node.label}.",
                    f"Benchmarked laboratory verification demonstrating operational principles."
                ],
                applications=[
                    f"High-reliability system design and simulation within {mindmap.title}.",
                    "Automated verification, analysis, and optimization pipelines."
                ],
                related_concepts=[
                    "Quantum Information Theory",
                    "State Vector Analysis",
                    "Computational Complexity"
                ],
                model_name="dev-fallback-engine",
                version=1,
            )
            db.add(fallback_explanation)
            await db.commit()
            await db.refresh(fallback_explanation)
            return fallback_explanation
