import asyncio
import time
from typing import Any, Literal

from pydantic import BaseModel

from oxylabs_ai_studio.client import OxyStudioAIClient
from oxylabs_ai_studio.logger import get_logger
from oxylabs_ai_studio.models import SchemaResponse

SCRAPE_TIMEOUT_SECONDS = 60 * 3
POLL_INTERVAL_SECONDS = 5
POLL_MAX_ATTEMPTS = SCRAPE_TIMEOUT_SECONDS // POLL_INTERVAL_SECONDS

logger = get_logger(__name__)


class AiScraperJob(BaseModel):
    run_id: str
    message: str | None = None
    data: dict[str, Any] | str | None


class AiScraper(OxyStudioAIClient):
    """AI Scraper app."""

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)

    def scrape(
        self,
        url: str,
        output_format: Literal[
            "json", "markdown", "csv", "screenshot", "toon"
        ] = "markdown",
        schema: dict[str, Any] | None = None,
        render_javascript: bool | Literal["auto"] = False,
        geo_location: str | None = None,
        user_agent: str | None = None,
    ) -> AiScraperJob:
        if output_format in ["json", "csv", "toon"] and schema is None:
            raise ValueError(
                "openapi_schema is required when output_format is json, csv or toon.",
            )

        body = {
            "url": url,
            "output_format": output_format,
            "openapi_schema": schema,
            "render_javascript": render_javascript,
            "geo_location": geo_location,
            "user_agent": user_agent,
        }
        client = self.get_client()
        create_response = self.call_api(
            client=client, url="/scrape", method="POST", body=body
        )
        if create_response.status_code != 200:
            raise Exception(
                f"Failed to create scrape job for {url}: {create_response.text}"
            )
        resp_body = create_response.json()
        run_id = resp_body["run_id"]
        try:
            for _ in range(POLL_MAX_ATTEMPTS):
                try:
                    get_response = self.call_api(
                        client=client,
                        url="/scrape/run/data",
                        method="GET",
                        params={"run_id": run_id},
                    )
                except Exception:
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue
                if get_response.status_code != 200:
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue
                resp_body = get_response.json()
                if resp_body["status"] == "completed":
                    data = resp_body.get("data", None)
                    return AiScraperJob(
                        run_id=run_id,
                        message=resp_body.get("error_code", None),
                        data=data,
                    )
                if resp_body["status"] == "failed":
                    return AiScraperJob(
                        run_id=run_id,
                        message=resp_body.get("error_code", None),
                        data=None,
                    )
                time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("[Cancelled] Scraping was cancelled by user.")
            raise KeyboardInterrupt from None
        except Exception as e:
            raise e
        raise TimeoutError(f"Failed to scrape {url}: timeout.")

    def generate_schema(self, prompt: str) -> dict[str, Any] | None:
        logger.info("Generating schema")
        body = {"user_prompt": prompt}
        response = self.call_api(
            client=self.get_client(), url="/scrape/schema", method="POST", body=body
        )
        if response.status_code != 200:
            raise Exception(f"Failed to generate schema: {response.text}")
        json_response: SchemaResponse = response.json()
        return json_response.get("openapi_schema", None)

    async def scrape_async(
        self,
        url: str,
        output_format: Literal[
            "json", "markdown", "csv", "screenshot", "toon"
        ] = "markdown",
        schema: dict[str, Any] | None = None,
        render_javascript: bool | Literal["auto"] = False,
        geo_location: str | None = None,
        user_agent: str | None = None,
    ) -> AiScraperJob:
        """Async version of scrape."""
        if output_format in ["json", "csv", "toon"] and schema is None:
            raise ValueError(
                "openapi_schema is required when output_format is json, csv or toon.",
            )

        body = {
            "url": url,
            "output_format": output_format,
            "openapi_schema": schema,
            "render_javascript": render_javascript,
            "geo_location": geo_location,
            "user_agent": user_agent,
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
                    try:
                        get_response = await self.call_api_async(
                            client=client,
                            url="/scrape/run/data",
                            method="GET",
                            params={"run_id": run_id},
                        )
                    except Exception:
                        await asyncio.sleep(POLL_INTERVAL_SECONDS)
                        continue
                    if get_response.status_code != 200:
                        await asyncio.sleep(POLL_INTERVAL_SECONDS)
                        continue
                    resp_body = get_response.json()
                    if resp_body["status"] == "completed":
                        data = resp_body.get("data", None)
                        return AiScraperJob(
                            run_id=run_id,
                            message=resp_body.get("error_code", None),
                            data=data,
                        )
                    if resp_body["status"] == "failed":
                        return AiScraperJob(
                            run_id=run_id,
                            message=resp_body.get("error_code", None),
                            data=None,
                        )
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                logger.info("[Cancelled] Scraping was cancelled by user.")
                raise KeyboardInterrupt from None
            except Exception as e:
                raise e
            raise TimeoutError(f"Failed to scrape {url}: timeout.")

    async def generate_schema_async(self, prompt: str) -> dict[str, Any] | None:
        """Async version of generate_schema. Uses httpx.AsyncClient."""
        logger.info("Generating schema (async)")
        body = {"user_prompt": prompt}
        async with self.async_client() as client:
            response = await self.call_api_async(
                client=client, url="/scrape/schema", method="POST", body=body
            )
            if response.status_code != 200:
                raise Exception(f"Failed to generate schema: {response.text}")
            json_response: SchemaResponse = response.json()
            return json_response.get("openapi_schema", None)
