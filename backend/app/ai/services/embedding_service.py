"""Vector embeddings generation service using Gemini with fallback capabilities."""

import hashlib
import logging
import math
from app.ai.providers.gemini import GeminiProvider, get_gemini_provider

logger = logging.getLogger("mindweave.ai.embeddings")


class EmbeddingService:
    """Generates 768-dimensional float embeddings for semantic text chunks."""

    def __init__(self, provider: GeminiProvider | None = None) -> None:
        self.provider = provider or get_gemini_provider()

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate a 768-dimensional vector embedding for the given text."""
        client = self.provider.get_client()

        if client is not None:
            try:
                # Use Google GenAI embeddings model
                result = client.models.embed_content(
                    model="text-embedding-004",
                    contents=text,
                )
                if result and hasattr(result, "embeddings") and result.embeddings:
                    values = result.embeddings[0].values
                    if values and len(values) == 768:
                        return list(values)
            except Exception as exc:
                logger.warning("Gemini embedding API call failed: %s. Using deterministic fallback embedding.", exc)

        # Deterministic 768-dim normalized embedding fallback
        return self._generate_fallback_embedding(text)

    def _generate_fallback_embedding(self, text: str) -> list[float]:
        """Generate a deterministic, unit-normalized 768-dim float vector from text hash."""
        vector = []
        for i in range(768):
            seed_bytes = f"{text}:{i}".encode("utf-8")
            h = int(hashlib.sha256(seed_bytes).hexdigest()[:8], 16)
            val = (h / 0xFFFFFFFF) * 2.0 - 1.0
            vector.append(val)

        # Normalize vector to unit length
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector
