import asyncio
import time
from typing import Any, Literal

import httpx
from pydantic import BaseModel

from oxylabs_ai_studio.client import OxyStudioAIClient
from oxylabs_ai_studio.logger import get_logger
from oxylabs_ai_studio.models import SchemaResponse

SCRAPE_TIMEOUT_SECONDS = 60 * 3
POLL_INTERVAL_SECONDS = 3
POLL_MAX_ATTEMPTS = SCRAPE_TIMEOUT_SECONDS // POLL_INTERVAL_SECONDS

logger = get_logger(__name__)


class AiScraperJob(BaseModel):
    run_id: str
    message: str | None = None
    data: dict[str, Any] | str | None


class AiScraper(OxyStudioAIClient):
    """AI Scraper app."""

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def scrape(
        self,
        url: str,
        output_format: Literal["json", "markdown"] = "markdown",
        schema: dict[str, Any] | None = None,
        render_javascript: bool = False,
    ) -> AiScraperJob:
        if output_format == "json" and schema is None:
            raise ValueError("openapi_schema is required when output_format is json")

        body = {
            "url": url,
            "output_format": output_format,
            "openapi_schema": schema,
            "render_html": render_javascript,
        }
        create_response = self.client.post(url="/scrape", json=body)
        if create_response.status_code != 200:
            raise Exception(
                f"Failed to create scrape job for {url}: {create_response.text}"
            )
        resp_body = create_response.json()
        run_id = resp_body["run_id"]
        try:
            for _ in range(POLL_MAX_ATTEMPTS):
                get_response = self.client.get("/scrape/run", params={"run_id": run_id})
                if get_response.status_code != 200:
                    raise Exception(f"Failed to scrape {url}: {get_response.text}")
                resp_body = get_response.json()
                if resp_body["status"] == "completed":
                    return AiScraperJob(
                        run_id=run_id,
                        message=resp_body.get("message", None),
                        data=self._get_data(run_id=run_id),
                    )
                if resp_body["status"] == "failed":
                    raise Exception(f"Failed to scrape {url}.")
                time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("[Cancelled] Scraping was cancelled by user.")
            raise KeyboardInterrupt from None
        except Exception as e:
            raise e
        raise TimeoutError(f"Failed to scrape {url}: timeout.")

    def _get_data(self, run_id: str) -> dict[str, Any]:
        get_response = self.client.get("/scrape/run/data", params={"run_id": run_id})
        if get_response.status_code != 200:
            raise Exception(f"Failed to get data for run {run_id}: {get_response.text}")
        return get_response.json().get("data", {}) or {}

    def generate_schema(self, prompt: str) -> dict[str, Any] | None:
        logger.info("Generating schema")
        body = {"user_prompt": prompt}
        response = self.client.post(url="/scrape/schema", json=body)
        if response.status_code != 200:
            raise Exception(f"Failed to generate schema: {response.text}")
        json_response: SchemaResponse = response.json()
        return json_response.get("openapi_schema", None)

    async def scrape_async(
        self,
        url: str,
        output_format: Literal["json", "markdown"] = "markdown",
        schema: dict[str, Any] | None = None,
        render_javascript: bool = False,
    ) -> AiScraperJob:
        """Async version of scrape."""
        if output_format == "json" and schema is None:
            raise ValueError("openapi_schema is required when output_format is json")

        body = {
            "url": url,
            "output_format": output_format,
            "openapi_schema": schema,
            "render_html": render_javascript,
        }
        async with self.async_client() as client:
            create_response = await client.post(url="/scrape", json=body)
            if create_response.status_code != 200:
                raise Exception(
                    f"Failed to create scrape job for {url}: {create_response.text}"
                )
            resp_body = create_response.json()
            run_id = resp_body["run_id"]
            try:
                for _ in range(POLL_MAX_ATTEMPTS):
                    get_response = await client.get(
                        "/scrape/run", params={"run_id": run_id}
                    )
                    if get_response.status_code != 200:
                        raise Exception(f"Failed to scrape {url}: {get_response.text}")
                    resp_body = get_response.json()
                    if resp_body["status"] == "completed":
                        data = await self.get_data_async(client, run_id=run_id)
                        return AiScraperJob(
                            run_id=run_id,
                            message=resp_body.get("message", None),
                            data=data,
                        )
                    if resp_body["status"] == "failed":
                        raise Exception(f"Failed to scrape {url}.")
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                logger.info("[Cancelled] Scraping was cancelled by user.")
                raise KeyboardInterrupt from None
            except Exception as e:
                raise e
            raise TimeoutError(f"Failed to scrape {url}: timeout.")

    async def get_data_async(
        self, client: httpx.AsyncClient, run_id: str
    ) -> dict[str, Any]:
        get_response = await client.get("/scrape/run/data", params={"run_id": run_id})
        if get_response.status_code != 200:
            raise Exception(f"Failed to get data for run {run_id}: {get_response.text}")
        return get_response.json().get("data", {}) or {}

    async def generate_schema_async(self, prompt: str) -> dict[str, Any] | None:
        """Async version of generate_schema. Uses httpx.AsyncClient."""
        logger.info("Generating schema (async)")
        body = {"user_prompt": prompt}
        async with self.async_client() as client:
            response = await client.post(url="/scrape/schema", json=body)
            if response.status_code != 200:
                raise Exception(f"Failed to generate schema: {response.text}")
            json_response: SchemaResponse = response.json()
            return json_response.get("openapi_schema", None)
