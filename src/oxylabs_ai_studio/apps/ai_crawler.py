import asyncio
import time
from typing import Any, Literal

from pydantic import BaseModel

from oxylabs_ai_studio.client import OxyStudioAIClient
from oxylabs_ai_studio.logger import get_logger
from oxylabs_ai_studio.models import SchemaResponse

CRAWLER_TIMEOUT_SECONDS = 60 * 10
POLL_INTERVAL_SECONDS = 3
POLL_MAX_ATTEMPTS = CRAWLER_TIMEOUT_SECONDS // POLL_INTERVAL_SECONDS

logger = get_logger(__name__)


class AiCrawlerJob(BaseModel):
    run_id: str
    message: str | None = None
    data: list[dict[str, Any]] | list[str] | None = None


class AiCrawler(OxyStudioAIClient):
    """AI Crawl app."""

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)

    def crawl(
        self,
        url: str,
        user_prompt: str,
        output_format: Literal["json", "markdown"] = "markdown",
        schema: dict[str, Any] | None = None,
        render_javascript: bool = False,
        return_sources_limit: int = 25,
    ) -> AiCrawlerJob:
        if output_format == "json" and schema is None:
            raise ValueError("openapi_schema is required when output_format is json")

        body = {
            "domain": url,
            "user_prompt": user_prompt,
            "output_format": output_format,
            "openapi_schema": schema,
            "auxiliary_prompt": user_prompt,
            "render_html": render_javascript,
            "return_sources_limit": return_sources_limit,
        }
        create_response = self.client.post(url="/extract/run", json=body)
        if create_response.status_code != 200:
            raise Exception(
                f"Failed to create crawl job for {url}: {create_response.text}"
            )
        resp_body = create_response.json()
        run_id = resp_body["run_id"]
        logger.info(f"Starting crawl for url: {url}. Job id: {run_id}.")
        try:
            for _ in range(POLL_MAX_ATTEMPTS):
                get_response = self.client.get(
                    "/extract/run/data", params={"run_id": run_id}
                )
                if get_response.status_code == 202:
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue
                if get_response.status_code != 200:
                    raise Exception(f"Failed to crawl {url}: {get_response.text}")
                resp_body = get_response.json()
                if resp_body["status"] == "processing":
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue
                if resp_body["status"] == "completed":
                    return AiCrawlerJob(
                        run_id=run_id,
                        message=resp_body.get("message", None),
                        data=resp_body["data"],
                    )
                if resp_body["status"] == "failed":
                    raise Exception(f"Failed to crawl {url}.")
                time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("[Cancelled] Crawling was cancelled by user.")
            raise KeyboardInterrupt from None
        raise TimeoutError(f"Failed to crawl {url}: timeout.")

    def generate_schema(self, prompt: str) -> dict[str, Any] | None:
        logger.info("Generating schema")
        body = {"user_prompt": prompt}
        response = self.client.post(url="/extract/generate-params", json=body)
        if response.status_code != 200:
            raise Exception(f"Failed to generate schema: {response.text}")
        json_response: SchemaResponse = response.json()
        return json_response.get("openapi_schema", None)

    async def crawl_async(
        self,
        url: str,
        user_prompt: str = "",
        output_format: Literal["json", "markdown"] = "markdown",
        schema: dict[str, Any] | None = None,
        render_javascript: bool = False,
        return_sources_limit: int = 25,
    ) -> AiCrawlerJob:
        """Async version of crawl."""
        if output_format == "json" and schema is None:
            raise ValueError("openapi_schema is required when output_format is json")

        body = {
            "domain": url,
            "user_prompt": user_prompt,
            "output_format": output_format,
            "openapi_schema": schema,
            "auxiliary_prompt": user_prompt,
            "render_html": render_javascript,
            "return_sources_limit": return_sources_limit,
        }
        async with self.async_client() as client:
            create_response = await client.post(url="/extract/run", json=body)
            if create_response.status_code != 200:
                raise Exception(
                    f"Failed to create crawl job for {url}: {create_response.text}"
                )
            resp_body = create_response.json()
            run_id = resp_body["run_id"]
            logger.info(f"Starting async crawl for url: {url}. Job id: {run_id}.")
            try:
                for _ in range(POLL_MAX_ATTEMPTS):
                    get_response = await client.get(
                        "/extract/run/data", params={"run_id": run_id}
                    )
                    if get_response.status_code == 202:
                        await asyncio.sleep(POLL_INTERVAL_SECONDS)
                        continue
                    if get_response.status_code != 200:
                        raise Exception(f"Failed to crawl {url}: {get_response.text}")
                    resp_body = get_response.json()
                    if resp_body["status"] == "processing":
                        await asyncio.sleep(POLL_INTERVAL_SECONDS)
                        continue
                    if resp_body["status"] == "completed":
                        return AiCrawlerJob(
                            run_id=run_id,
                            message=resp_body.get("message", None),
                            data=resp_body["data"],
                        )
                    if resp_body["status"] == "failed":
                        raise Exception(f"Failed to crawl {url}.")
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                logger.info("[Cancelled] Crawling was cancelled by user.")
                raise KeyboardInterrupt from None
            raise TimeoutError(f"Failed to crawl {url}: timeout.")

    async def generate_schema_async(self, prompt: str) -> dict[str, Any] | None:
        """Async version of generate_schema. Uses httpx.AsyncClient."""
        logger.info("Generating schema (async)")
        body = {"user_prompt": prompt}
        async with self.async_client() as client:
            response = await client.post(url="/extract/generate-params", json=body)
            if response.status_code != 200:
                raise Exception(f"Failed to generate schema: {response.text}")
            json_response: SchemaResponse = response.json()
            return json_response.get("openapi_schema", None)
