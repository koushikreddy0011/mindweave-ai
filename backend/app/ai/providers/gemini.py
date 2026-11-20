"""Google Gemini AI client provider wrapper using the official google-genai SDK."""

import asyncio
import logging
import time
from typing import Any

from google import genai

from app.core.config import settings

logger = logging.getLogger("mindweave.ai.provider")


class GeminiProvider:
    """Client wrapper for Google Gemini API operations."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
    ) -> None:
        raw_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.api_key = raw_key.strip() if raw_key else ""
        self.model_name = model_name if model_name is not None else settings.GEMINI_MODEL
        self.client: genai.Client | None = None

        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                logger.error("Failed to initialize Google Gemini client: %s", exc)
                self.client = None
        else:
            logger.warning("GEMINI_API_KEY is not configured or is empty. Development fallback mode enabled.")

    def get_client(self) -> genai.Client | None:
        """Return the underlying genai.Client instance, or None if unconfigured."""
        return self.client

    async def ping(self) -> dict[str, Any]:
        """Test Gemini API connectivity, key validity, and model latency."""
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured or client failed to initialize")

        start_time = time.perf_counter()

        if hasattr(self.client, "aio") and hasattr(self.client.aio, "models"):
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents="Reply with only the word: PONG",
            )
        else:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents="Reply with only the word: PONG",
            )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response_text = response.text or ""

        return {
            "status": "connected",
            "model": self.model_name,
            "latency_ms": latency_ms,
            "response": response_text.strip(),
        }


_gemini_provider_instance: GeminiProvider | None = None


def get_gemini_provider() -> GeminiProvider:
    """Factory providing a singleton GeminiProvider instance."""
    global _gemini_provider_instance
    if _gemini_provider_instance is None:
        _gemini_provider_instance = GeminiProvider()
    return _gemini_provider_instance
