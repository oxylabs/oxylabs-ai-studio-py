from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Literal

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    RetryError,
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from oxylabs_ai_studio.logger import get_logger
from oxylabs_ai_studio.settings import settings

logger = get_logger(__name__)

_UA_API: str | None = None
DEFAULT_RETRIES = 5


def _resolve_ua() -> str:
    return (
        _UA_API.strip() if isinstance(_UA_API, str) and _UA_API.strip() else None
    ) or "python-sdk"


def _is_retryable_exception(exception: BaseException) -> bool:
    if isinstance(exception, httpx.HTTPStatusError):
        status = exception.response.status_code
        if status == 429 or 500 <= status < 600:
            return True
    return False


def _before_sleep_warn(state: RetryCallState) -> None:
    exc = state.outcome.exception() if state.outcome is not None else None
    if (
        isinstance(exc, httpx.HTTPStatusError)
        and getattr(exc, "response", None) is not None
        and exc.response.status_code == 429
    ):
        logger.warning(
            f"Rate limit (HTTP 429). Consider reducing request rate. "
            f"(attempt {state.attempt_number})"
        )
        return


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

    def get_client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": _resolve_ua(),
            },
            timeout=self.timeout,
        )

    @asynccontextmanager
    async def async_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Async context manager for async client."""
        async_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": _resolve_ua(),
            },
            timeout=self.timeout,
        )
        try:
            yield async_client
        finally:
            await async_client.aclose()

    async def call_api_async(
        self,
        client: httpx.AsyncClient,
        url: str,
        method: Literal["GET", "POST"],
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        retries: int = DEFAULT_RETRIES,
    ) -> httpx.Response:
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(retries),
                wait=wait_exponential(multiplier=1, min=1, max=8),
                retry=retry_if_exception(_is_retryable_exception),
                reraise=True,
                before_sleep=_before_sleep_warn,
            ):
                with attempt:
                    response = await client.request(
                        method, url, json=body, params=params
                    )
                    response.raise_for_status()
                    return response
        except RetryError as retry_error:
            exc = retry_error.last_attempt.exception()
            logger.error(f"Failed calling API after {retries} attempts {url}: {exc}")
            raise Exception(str(exc)) from None
        except Exception as exc:
            logger.exception(
                f"Failed calling API after {retries} attempts {url}: {exc}"
            )
            raise exc

        raise RuntimeError("Unreachable state in call_api_async")

    def call_api(
        self,
        client: httpx.Client,
        url: str,
        method: Literal["GET", "POST"],
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        retries: int = DEFAULT_RETRIES,
    ) -> httpx.Response:
        try:
            for attempt in Retrying(
                stop=stop_after_attempt(retries),
                wait=wait_exponential(multiplier=1, min=1, max=8),
                retry=retry_if_exception(_is_retryable_exception),
                reraise=True,
                before_sleep=_before_sleep_warn,
            ):
                with attempt:
                    response = client.request(method, url, json=body, params=params)
                    response.raise_for_status()
                    return response
        except RetryError as retry_error:
            exc = retry_error.last_attempt.exception()
            logger.error(f"Failed calling API after {retries} attempts {url}: {exc}")
            raise Exception(str(exc)) from None
        except Exception as exc:
            logger.exception(
                f"Failed calling API after {retries} attempts {url}: {exc}"
            )
            raise exc

        raise RuntimeError("Unreachable state in call_api")
