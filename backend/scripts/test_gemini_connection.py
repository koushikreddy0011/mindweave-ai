"""Validation script for testing Google Gemini API connectivity and credentials."""

import asyncio
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ai.providers import GeminiProvider
from app.core.config import settings


async def run_gemini_test() -> int:
    """Verify Gemini API key configuration and model connectivity."""
    print("=" * 60)
    print("MindWeave AI — Google Gemini Connectivity Verification")
    print("=" * 60)

    # 1. Check if GEMINI_API_KEY is configured
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.strip() == "":
        print("\n[WARNING] GEMINI_API_KEY is not set in backend/.env.")
        print("Please obtain an API key from https://aistudio.google.com")
        print('and add GEMINI_API_KEY="your-api-key-here" to backend/.env.\n')
        print("=" * 60)
        return 1

    print(f"[+] Configured Model: {settings.GEMINI_MODEL}")
    print("[+] Sending ping request to Gemini API...")

    try:
        provider = GeminiProvider()
        result = await provider.ping()

        print(f"  [✓] Connection Status: {result['status']}")
        print(f"  [✓] Model: {result['model']}")
        print(f"  [✓] Latency: {result['latency_ms']} ms")
        print(f"  [✓] Response: '{result['response']}'")

        print("\n" + "=" * 60)
        print("[SUCCESS] Google Gemini API connection verified successfully!")
        print("=" * 60)
        return 0

    except Exception as exc:
        print(f"\n[ERROR] Gemini API connection failed: {exc}")
        print("\nTroubleshooting:")
        print("  1. Verify the API key at https://aistudio.google.com")
        print("  2. Check if your network has access to generativelanguage.googleapis.com")
        print("  3. Verify the model name in settings (e.g. gemini-3.6-flash, gemini-2.5-flash, gemini-1.5-flash)")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_gemini_test())
    sys.exit(exit_code)
