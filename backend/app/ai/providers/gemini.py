"""Google Gemini AI client provider wrapper with multi-key rotation and failover capabilities."""

import asyncio
import logging
import time
from typing import Any

from google import genai

from app.core.config import settings

logger = logging.getLogger("mindweave.ai.provider")


class GeminiProvider:
    """Client wrapper managing single or multi-key Google Gemini API client pools."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
    ) -> None:
        self.model_name = model_name if model_name is not None else settings.GEMINI_MODEL
        self.clients: list[genai.Client] = []
        self._current_index = 0

        # Collect and merge all configured keys without duplicates
        raw_keys: list[str] = []
        if api_key and api_key.strip():
            raw_keys.append(api_key.strip())
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            raw_keys.append(settings.GEMINI_API_KEY.strip())
        if settings.GEMINI_API_KEYS and settings.GEMINI_API_KEYS.strip():
            raw_keys.extend([k.strip() for k in settings.GEMINI_API_KEYS.split(",") if k.strip()])
        # Deduplicate while preserving order
        keys = list(dict.fromkeys(raw_keys))

        for idx, k in enumerate(keys):
            try:
                c = genai.Client(api_key=k)
                self.clients.append(c)
            except Exception as exc:
                logger.error("Failed to initialize Gemini client for key #%d: %s", idx + 1, exc)

        if self.clients:
            logger.info("Initialized GeminiProvider with %d active API key(s)", len(self.clients))
        else:
            logger.warning("No valid Gemini API keys configured. High-fidelity development fallback engine active.")

    def get_client(self) -> genai.Client | None:
        """Return the active genai.Client instance, or None if unconfigured."""
        if not self.clients:
            return None
        return self.clients[self._current_index % len(self.clients)]

    def rotate_key(self) -> genai.Client | None:
        """Rotate to the next API key in the pool (used on 429/quota exhaustion)."""
        if len(self.clients) <= 1:
            return self.get_client()
        self._current_index = (self._current_index + 1) % len(self.clients)
        logger.info("Rotated to API key pool slot #%d of %d", self._current_index + 1, len(self.clients))
        return self.clients[self._current_index]

    async def ping(self) -> dict[str, Any]:
        """Test Gemini API connectivity, key validity, and model latency."""
        client = self.get_client()
        if not client:
            raise ValueError("GEMINI_API_KEY is not configured or client failed to initialize")

        start_time = time.perf_counter()

        if hasattr(client, "aio") and hasattr(client.aio, "models"):
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents="Reply with only the word: PONG",
            )
        else:
            response = await asyncio.to_thread(
                client.models.generate_content,
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
            "pool_size": len(self.clients),
        }


_gemini_provider_instance: GeminiProvider | None = None


def get_gemini_provider() -> GeminiProvider:
    """Factory providing a singleton GeminiProvider instance."""
    global _gemini_provider_instance
    if _gemini_provider_instance is None:
        _gemini_provider_instance = GeminiProvider()
    return _gemini_provider_instance
