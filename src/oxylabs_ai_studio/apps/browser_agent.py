import asyncio
import time
from typing import Any, Literal

from pydantic import BaseModel

from oxylabs_ai_studio.client import OxyStudioAIClient
from oxylabs_ai_studio.logger import get_logger
from oxylabs_ai_studio.models import SchemaResponse

BROWSER_AGENT_TIMEOUT_SECONDS = 60 * 10
POLL_INTERVAL_SECONDS = 5
POLL_MAX_ATTEMPTS = BROWSER_AGENT_TIMEOUT_SECONDS // POLL_INTERVAL_SECONDS

logger = get_logger(__name__)


class DataModel(BaseModel):
    type: Literal["json", "markdown", "html", "screenshot", "csv"]
    content: dict[str, Any] | str | None


class BrowserAgentJob(BaseModel):
    run_id: str
    message: str | None = None
    data: DataModel | None = None


class BrowserAgent(OxyStudioAIClient):
    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)

    def run(
        self,
        url: str,
        user_prompt: str = "",
        output_format: Literal[
            "json", "markdown", "html", "screenshot", "csv"
        ] = "markdown",
        schema: dict[str, Any] | None = None,
        geo_location: str | None = None,
    ) -> BrowserAgentJob:
        if output_format in ["json", "csv"] and schema is None:
            raise ValueError(
                "openapi_schema is required when output_format is json or csv.",
            )

        body = {
            "url": url,
            "output_format": output_format,
            "openapi_schema": schema,
            "auxiliary_prompt": user_prompt,
            "geo_location": geo_location,
        }
        client = self.get_client()
        create_response = self.call_api(
            client=client, url="/browser-agent/run", method="POST", body=body
        )
        if create_response.status_code != 200:
            raise Exception(f"Failed to launch browser agent: {create_response.text}")
        resp_body = create_response.json()
        run_id = resp_body["run_id"]
        logger.info(f"Starting browser agent run for url: {url}. Job id: {run_id}.")
        try:
            for _ in range(POLL_MAX_ATTEMPTS):
                try:
                    get_response = self.call_api(
                        client=client,
                        url="/browser-agent/run/data",
                        method="GET",
                        params={"run_id": run_id},
                    )
                except Exception:
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue
                if get_response.status_code == 202:
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue
                if get_response.status_code != 200:
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue
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
                    return BrowserAgentJob(
                        run_id=run_id,
                        message=resp_body.get("error_code", None),
                        data=None,
                    )
                time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("[Cancelled] Browser agent was cancelled by user.")
            raise KeyboardInterrupt from None
        raise TimeoutError(f"Failed to scrape {url}: timeout.")

    def generate_schema(self, prompt: str) -> dict[str, Any] | None:
        logger.info("Generating schema")
        body = {"user_prompt": prompt}
        response = self.call_api(
            client=self.get_client(),
            url="/browser-agent/generate-params",
            method="POST",
            body=body,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to generate schema: {response.text}")
        json_response: SchemaResponse = response.json()
        return json_response.get("openapi_schema", None)

    async def run_async(
        self,
        url: str,
        user_prompt: str = "",
        output_format: Literal[
            "json",
            "markdown",
            "html",
            "screenshot",
            "csv",
        ] = "markdown",
        schema: dict[str, Any] | None = None,
        geo_location: str | None = None,
    ) -> BrowserAgentJob:
        """Async version of run."""
        if output_format in ["json", "csv"] and schema is None:
            raise ValueError(
                "openapi_schema is required when output_format is json or csv.",
            )

        body = {
            "url": url,
            "output_format": output_format,
            "openapi_schema": schema,
            "auxiliary_prompt": user_prompt,
            "geo_location": geo_location,
        }
        async with self.async_client() as client:
            create_response = await self.call_api_async(
                client=client, url="/browser-agent/run", method="POST", body=body
            )
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
                    try:
                        get_response = await self.call_api_async(
                            client=client,
                            url="/browser-agent/run/data",
                            method="GET",
                            params={"run_id": run_id},
                        )
                    except Exception:
                        await asyncio.sleep(POLL_INTERVAL_SECONDS)
                        continue
                    if get_response.status_code == 202:
                        await asyncio.sleep(POLL_INTERVAL_SECONDS)
                        continue
                    if get_response.status_code != 200:
                        await asyncio.sleep(POLL_INTERVAL_SECONDS)
                        continue
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
                        return BrowserAgentJob(
                            run_id=run_id,
                            message=resp_body.get("error_code", None),
                            data=None,
                        )
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
            response = await self.call_api_async(
                client=client,
                url="/browser-agent/generate-params",
                method="POST",
                body=body,
            )
            if response.status_code != 200:
                raise Exception(f"Failed to generate schema: {response.text}")
            json_response: SchemaResponse = response.json()
            return json_response.get("openapi_schema", None)
