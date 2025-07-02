import asyncio
import time
from typing import Any, Literal

from pydantic import BaseModel

from oxylabs_ai_studio.client import OxyStudioAIClient
from oxylabs_ai_studio.logger import get_logger
from oxylabs_ai_studio.models import SchemaResponse

BROWSER_AGENT_TIMEOUT_SECONDS = 60 * 10
POLL_INTERVAL_SECONDS = 3
POLL_MAX_ATTEMPTS = BROWSER_AGENT_TIMEOUT_SECONDS // POLL_INTERVAL_SECONDS

logger = get_logger(__name__)


class DataModel(BaseModel):
    type: Literal["json", "markdown", "html", "screenshot"]
    content: dict[str, Any] | str | None


class BrowserAgentJob(BaseModel):
    run_id: str
    message: str | None = None
    data: DataModel | None = None


class BrowserAgent(OxyStudioAIClient):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def run(
        self,
        url: str,
        user_prompt: str = "",
        output_format: Literal["json", "markdown", "html", "screenshot"] = "markdown",
        schema: dict[str, Any] | None = None,
    ) -> BrowserAgentJob:
        if output_format == "json" and schema is None:
            raise ValueError("openapi_schema is required when output_format is json")

        body = {
            "url": url,
            "output_format": output_format,
            "openapi_schema": schema,
            "auxiliary_prompt": user_prompt,
        }
        create_response = self.client.post(url="/browser-agent/run", json=body)
        if create_response.status_code != 200:
            raise Exception(f"Failed to launch browser agent: {create_response.text}")
        resp_body = create_response.json()
        run_id = resp_body["run_id"]
        logger.info(f"Starting browser agent run for url: {url}. Job id: {run_id}.")
        try:
            for _ in range(POLL_MAX_ATTEMPTS):
                get_response = self.client.get(
                    "/browser-agent/run/data", params={"run_id": run_id}
                )
                if get_response.status_code == 202:
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue
                if get_response.status_code != 200:
                    raise Exception(f"Failed to scrape {url}: {get_response.text}")
                resp_body = get_response.json()
                if resp_body["status"] == "processing":
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue
                if resp_body["status"] == "completed":
                    return BrowserAgentJob(
                        run_id=run_id,
                        message=resp_body.get("message", None),
                        data=resp_body["data"],
                    )
                if resp_body["status"] == "failed":
                    raise Exception(f"Failed to scrape {url}.")
                time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("[Cancelled] Browser agent was cancelled by user.")
            raise KeyboardInterrupt from None
        raise TimeoutError(f"Failed to scrape {url}: timeout.")

    def generate_schema(self, prompt: str) -> dict[str, Any] | None:
        logger.info("Generating schema")
        body = {"user_prompt": prompt}
        response = self.client.post(url="/browser-agent/generate-params", json=body)
        if response.status_code != 200:
            raise Exception(f"Failed to generate schema: {response.text}")
        json_response: SchemaResponse = response.json()
        return json_response.get("openapi_schema", None)

    async def run_async(
        self,
        url: str,
        user_prompt: str = "",
        output_format: Literal["json", "markdown", "html", "screenshot"] = "markdown",
        schema: dict[str, Any] | None = None,
    ) -> BrowserAgentJob:
        """Async version of run."""
        if output_format == "json" and schema is None:
            raise ValueError("openapi_schema is required when output_format is json")

        body = {
            "url": url,
            "output_format": output_format,
            "openapi_schema": schema,
            "auxiliary_prompt": user_prompt,
        }
        async with self.async_client() as client:
            create_response = await client.post(url="/browser-agent/run", json=body)
            if create_response.status_code != 200:
                raise Exception(
                    f"Failed to launch browser agent: {create_response.text}"
                )
            resp_body = create_response.json()
            run_id = resp_body["run_id"]
            logger.info(
                f"Starting async browser agent run for url: {url}. Job id: {run_id}."
            )
            try:
                for _ in range(POLL_MAX_ATTEMPTS):
                    get_response = await client.get(
                        "/browser-agent/run/data", params={"run_id": run_id}
                    )
                    if get_response.status_code == 202:
                        await asyncio.sleep(POLL_INTERVAL_SECONDS)
                        continue
                    if get_response.status_code != 200:
                        raise Exception(f"Failed to scrape {url}: {get_response.text}")
                    resp_body = get_response.json()
                    if resp_body["status"] == "processing":
                        await asyncio.sleep(POLL_INTERVAL_SECONDS)
                        continue
                    if resp_body["status"] == "completed":
                        return BrowserAgentJob(
                            run_id=run_id,
                            message=resp_body.get("message", None),
                            data=resp_body["data"],
                        )
                    if resp_body["status"] == "failed":
                        raise Exception(f"Failed to scrape {url}.")
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                logger.info("[Cancelled] Browser agent was cancelled by user.")
                raise KeyboardInterrupt from None
            raise TimeoutError(f"Failed to scrape {url}: timeout.")

    async def generate_schema_async(self, prompt: str) -> dict[str, Any] | None:
        """Async version of generate_schema. Uses httpx.AsyncClient."""
        logger.info("Generating schema (async)")
        body = {"user_prompt": prompt}
        async with self.async_client() as client:
            response = await client.post(
                url="/browser-agent/generate-params", json=body
            )
            if response.status_code != 200:
                raise Exception(f"Failed to generate schema: {response.text}")
            json_response: SchemaResponse = response.json()
            return json_response.get("openapi_schema", None)
