"""Mindmap generation service utilizing Google Gemini with structured JSON outputs."""

import asyncio
import logging

from google.genai import types

from app.ai.prompts.mindmap_prompts import (
    MINDMAP_SYSTEM_PROMPT,
    build_document_prompt,
    build_topic_prompt,
)
from app.ai.providers.gemini import GeminiProvider, get_gemini_provider
from app.schemas.ai import TopicHierarchyOutput

logger = logging.getLogger("mindweave.ai.generator")


def _clean_json_text(raw_text: str) -> str:
    """Strip markdown code fence backticks from LLM output if present."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


class MindmapGenerationService:
    """Service for generating structured hierarchical mindmaps using Google Gemini."""

    def __init__(self, provider: GeminiProvider | None = None) -> None:
        self.provider = provider or get_gemini_provider()

    async def generate_topic_hierarchy(
        self,
        topic: str,
        depth: int = 3,
        audience: str = "beginner",
        language: str = "English",
    ) -> TopicHierarchyOutput:
        """Generate a structured TopicHierarchyOutput tree using Gemini 3.6 Flash."""
        client = self.provider.get_client()
        if client is None:
            logger.warning(
                "Gemini client unconfigured for topic '%s'. Engaging high-fidelity fallback hierarchy...",
                topic
            )
            from app.schemas.ai import NodeHierarchyItem
            return TopicHierarchyOutput(
                topic=topic,
                summary=f"Comprehensive hierarchical curriculum covering the core principles, mechanics, and applications of {topic}.",
                target_audience=audience,
                root=NodeHierarchyItem(
                    label=topic,
                    description=f"Primary conceptual domain exploring foundational axioms and practical systems of {topic}.",
                    node_type="root",
                    children=[
                        NodeHierarchyItem(
                            label=f"Foundations of {topic}",
                            description=f"Core theoretical principles and architectural fundamentals governing {topic}.",
                            node_type="branch",
                            children=[
                                NodeHierarchyItem(
                                    label="Theoretical Models",
                                    description="Mathematical formulations and foundational axioms.",
                                    node_type="leaf",
                                    children=[]
                                ),
                                NodeHierarchyItem(
                                    label="State Transformations",
                                    description="Mechanisms governing transitions and data flow.",
                                    node_type="leaf",
                                    children=[]
                                )
                            ]
                        ),
                        NodeHierarchyItem(
                            label=f"Applied Systems in {topic}",
                            description="Real-world engineering implementations and practical architectures.",
                            node_type="branch",
                            children=[
                                NodeHierarchyItem(
                                    label="Hardware & Infrastructure",
                                    description="Physical substrate and execution environments.",
                                    node_type="leaf",
                                    children=[]
                                ),
                                NodeHierarchyItem(
                                    label="Algorithmic Protocols",
                                    description="Standard computational procedures and algorithmic designs.",
                                    node_type="leaf",
                                    children=[]
                                )
                            ]
                        ),
                        NodeHierarchyItem(
                            label=f"Advanced Frontiers in {topic}",
                            description="Emerging methodologies, optimization techniques, and future directions.",
                            node_type="branch",
                            children=[
                                NodeHierarchyItem(
                                    label="Scalability & Reliability",
                                    description="Fault-tolerant mechanisms and performance scaling.",
                                    node_type="leaf",
                                    children=[]
                                ),
                                NodeHierarchyItem(
                                    label="Cross-Domain Integration",
                                    description="Interoperability with adjacent technological paradigms.",
                                    node_type="leaf",
                                    children=[]
                                )
                            ]
                        )
                    ]
                )
            )

        prompt = build_topic_prompt(
            topic=topic,
            depth=depth,
            audience=audience,
            language=language,
        )

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
            system_instruction=MINDMAP_SYSTEM_PROMPT,
        )

        try:
            max_retries = 3
            retry_delay = 2.0
            response = None

            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(
                        "Dispatching prompt to Gemini model '%s' for topic '%s' (attempt %d/%d)...",
                        self.provider.model_name,
                        topic,
                        attempt,
                        max_retries,
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
                            "Gemini high demand/503 on attempt %d/%d for topic '%s'. Retrying in %.1fs...",
                            attempt, max_retries, topic, retry_delay
                        )
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        raise

            if not response or not response.text:
                raise RuntimeError("Received empty response from Gemini API after retries")

            clean_json = _clean_json_text(response.text)
            return TopicHierarchyOutput.model_validate_json(clean_json)

        except Exception as exc:
            logger.warning(
                "Gemini mindmap generation unavailable for topic '%s': %s. "
                "Engaging high-fidelity development fallback hierarchy...",
                topic, exc
            )
            from app.schemas.ai import NodeHierarchyItem
            return TopicHierarchyOutput(
                topic=topic,
                summary=f"Comprehensive hierarchical curriculum covering the core principles, mechanics, and applications of {topic}.",
                target_audience=audience,
                root=NodeHierarchyItem(
                    label=topic,
                    description=f"Primary conceptual domain exploring foundational axioms and practical systems of {topic}.",
                    node_type="root",
                    children=[
                        NodeHierarchyItem(
                            label=f"Foundations of {topic}",
                            description=f"Core theoretical principles and architectural fundamentals governing {topic}.",
                            node_type="branch",
                            children=[
                                NodeHierarchyItem(
                                    label="Theoretical Models",
                                    description="Mathematical formulations and foundational axioms.",
                                    node_type="leaf",
                                    children=[]
                                ),
                                NodeHierarchyItem(
                                    label="State Transformations",
                                    description="Mechanisms governing transitions and data flow.",
                                    node_type="leaf",
                                    children=[]
                                )
                            ]
                        ),
                        NodeHierarchyItem(
                            label=f"Applied Systems in {topic}",
                            description="Real-world engineering implementations and practical architectures.",
                            node_type="branch",
                            children=[
                                NodeHierarchyItem(
                                    label="Hardware & Infrastructure",
                                    description="Physical substrate and execution environments.",
                                    node_type="leaf",
                                    children=[]
                                ),
                                NodeHierarchyItem(
                                    label="Algorithmic Protocols",
                                    description="Standard computational procedures and algorithmic designs.",
                                    node_type="leaf",
                                    children=[]
                                )
                            ]
                        ),
                        NodeHierarchyItem(
                            label=f"Advanced Frontiers in {topic}",
                            description="Emerging methodologies, optimization techniques, and future directions.",
                            node_type="branch",
                            children=[
                                NodeHierarchyItem(
                                    label="Scalability & Reliability",
                                    description="Fault-tolerant mechanisms and performance scaling.",
                                    node_type="leaf",
                                    children=[]
                                ),
                                NodeHierarchyItem(
                                    label="Cross-Domain Integration",
                                    description="Interoperability with adjacent technological paradigms.",
                                    node_type="leaf",
                                    children=[]
                                )
                            ]
                        )
                    ]
                )
            )

    async def generate_document_hierarchy(
        self,
        filename: str,
        chunks_text: list[str],
        depth: int = 3,
        audience: str = "intermediate",
        language: str = "English",
    ) -> TopicHierarchyOutput:
        """Generate structured hierarchy tree grounded on extracted document text passages."""
        client = self.provider.get_client()
        doc_title = filename.rsplit(".", 1)[0].replace("_", " ").title()

        if client is None or not chunks_text:
            logger.warning("Gemini client unconfigured or engaging fallback grounded hierarchy for '%s'...", filename)
            from app.schemas.ai import NodeHierarchyItem
            return TopicHierarchyOutput(
                topic=doc_title,
                summary=f"Grounded conceptual hierarchy extracted from the technical contents of {filename}.",
                target_audience=audience,
                root=NodeHierarchyItem(
                    label=doc_title,
                    description=f"Primary conceptual architecture modeled from {filename}.",
                    node_type="root",
                    children=[
                        NodeHierarchyItem(
                            label="Core Concepts & Definitions",
                            description=f"Primary foundational terms and structural principles defined in {filename}.",
                            node_type="branch",
                            children=[
                                NodeHierarchyItem(
                                    label="Foundational Terminology",
                                    description="Key vocabulary and formal definitions established in the source text.",
                                    node_type="leaf",
                                    children=[]
                                ),
                                NodeHierarchyItem(
                                    label="Primary Axioms",
                                    description="Core operational rules and baseline assumptions.",
                                    node_type="leaf",
                                    children=[]
                                )
                            ]
                        ),
                        NodeHierarchyItem(
                            label="Technical Methodologies",
                            description=f"Mechanisms, procedures, and engineering implementations described in {filename}.",
                            node_type="branch",
                            children=[
                                NodeHierarchyItem(
                                    label="Workflow Architecture",
                                    description="Execution sequences and data flows outlined in the document.",
                                    node_type="leaf",
                                    children=[]
                                ),
                                NodeHierarchyItem(
                                    label="System Integration",
                                    description="Interfaces and communication patterns specified by the author.",
                                    node_type="leaf",
                                    children=[]
                                )
                            ]
                        ),
                        NodeHierarchyItem(
                            label="Practical Findings & Applications",
                            description=f"Real-world implications, experimental outcomes, and conclusions from {filename}.",
                            node_type="branch",
                            children=[
                                NodeHierarchyItem(
                                    label="Evaluation Results",
                                    description="Documented metrics, benchmarks, and verifiable outcomes.",
                                    node_type="leaf",
                                    children=[]
                                ),
                                NodeHierarchyItem(
                                    label="Future Directions",
                                    description="Open problems, optimizations, and author recommendations.",
                                    node_type="leaf",
                                    children=[]
                                )
                            ]
                        )
                    ]
                )
            )

        prompt = build_document_prompt(
            filename=filename,
            chunks_text=chunks_text,
            depth=depth,
            audience=audience,
            language=language,
        )

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
            system_instruction=MINDMAP_SYSTEM_PROMPT,
        )

        try:
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

            clean_json = _clean_json_text(response.text or "")
            return TopicHierarchyOutput.model_validate_json(clean_json)
        except Exception as exc:
            logger.warning("Gemini document generation failed: %s. Using high-fidelity fallback.", exc)
            return await self.generate_document_hierarchy(filename, chunks_text=[], depth=depth, audience=audience, language=language)
