from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx

from oxylabs_ai_studio.logger import get_logger
from oxylabs_ai_studio.settings import settings

logger = get_logger(__name__)


class OxyStudioAIClient:
    """Main client for interacting with the Oxy Studio AI API."""

    def __init__(self, api_key: str | None = None, timeout: float = 30.0):
        """Initialize the client.

        Args:
            api_key: The API key for the Oxy Studio AI API.
            timeout: The timeout for the HTTP client.
        """
        resolved_key = api_key or settings.OXYLABS_AI_STUDIO_API_KEY
        if not resolved_key:
            raise ValueError("API key is required")
        self.api_key = resolved_key
        self.base_url = settings.OXYLABS_AI_STUDIO_API_URL
        self.timeout = timeout
        # Initialize HTTP client with proper headers
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "python-sdk",
            },
            timeout=timeout,
        )

    @asynccontextmanager
    async def async_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Async context manager for async client."""
        async_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "python-sdk",
            },
            timeout=self.timeout,
        )
        try:
            yield async_client
        finally:
            await async_client.aclose()
