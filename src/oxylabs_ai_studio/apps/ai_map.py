import asyncio
import time
from typing import Any

import httpx
from pydantic import BaseModel

from oxylabs_ai_studio.client import OxyStudioAIClient
from oxylabs_ai_studio.logger import get_logger

MAP_TIMEOUT_SECONDS = 60 * 5
POLL_INTERVAL_SECONDS = 5
POLL_MAX_ATTEMPTS = MAP_TIMEOUT_SECONDS // POLL_INTERVAL_SECONDS

logger = get_logger(__name__)


class AiMapJob(BaseModel):
    run_id: str
    message: str | None = None
    data: dict[str, Any] | list[str] | None


class AiMap(OxyStudioAIClient):
    """AI Map app."""

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)

    def map(
        self,
        url: str,
        user_prompt: str,
        return_sources_limit: int = 25,
        geo_location: str | None = None,
        render_javascript: bool = False,
    ) -> AiMapJob:
        body = {
            "url": url,
            "user_prompt": user_prompt,
            "return_sources_limit": return_sources_limit,
            "geo_location": geo_location,
            "render_html": render_javascript,
        }
        client = self.get_client()
        create_response = self.call_api(
            client=client, url="/map", method="POST", body=body
        )
        if create_response.status_code != 200:
            raise Exception(
                f"Failed to create map job for {url}: {create_response.text}"
            )
        resp_body = create_response.json()
        run_id = resp_body["run_id"]
        try:
            for _ in range(POLL_MAX_ATTEMPTS):
                try:
                    get_response = self.call_api(
                        client=client,
                        url="/map/run",
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
                    return AiMapJob(
                        run_id=run_id,
                        message=resp_body.get("message", None),
                        data=self._get_data(client=client, run_id=run_id),
                    )
                if resp_body["status"] == "failed":
                    return AiMapJob(
                        run_id=run_id,
                        message=resp_body.get("error_code", None),
                        data=None,
                    )
                time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("[Cancelled] Mapping was cancelled by user.")
            raise KeyboardInterrupt from None
        except Exception as e:
            raise e
        raise TimeoutError(f"Failed to map {url}: timeout.")

    def _get_data(self, client: httpx.Client, run_id: str) -> dict[str, Any]:
        get_response = self.call_api(
            client=client, url="/map/run/data", method="GET", params={"run_id": run_id}
        )
        if get_response.status_code != 200:
            raise Exception(f"Failed to get data for run {run_id}: {get_response.text}")
        return get_response.json().get("data", {}) or {}

    async def map_async(
        self,
        url: str,
        user_prompt: str,
        return_sources_limit: int = 25,
        geo_location: str | None = None,
        render_javascript: bool = False,
    ) -> AiMapJob:
        body = {
            "url": url,
            "user_prompt": user_prompt,
            "return_sources_limit": return_sources_limit,
            "geo_location": geo_location,
            "render_html": render_javascript,
        }
        async with self.async_client() as client:
            create_response = await self.call_api_async(
                client=client, url="/map", method="POST", body=body
            )
            if create_response.status_code != 200:
                raise Exception(
                    f"Failed to create map job for {url}: {create_response.text}"
                )
            resp_body = create_response.json()
            run_id = resp_body["run_id"]
            try:
                for _ in range(POLL_MAX_ATTEMPTS):
                    try:
                        get_response = await self.call_api_async(
                            client=client,
                            url="/map/run",
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
                        data = await self.get_data_async(client, run_id=run_id)
                        return AiMapJob(
                            run_id=run_id,
                            message=resp_body.get("message", None),
                            data=data,
                        )
                    if resp_body["status"] == "failed":
                        return AiMapJob(
                            run_id=run_id,
                            message=resp_body.get("error_code", None),
                            data=None,
                        )
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                logger.info("[Cancelled] Mapping was cancelled by user.")
                raise KeyboardInterrupt from None
            except Exception as e:
                raise e
            raise TimeoutError(f"Failed to map {url}: timeout.")

    async def get_data_async(
        self, client: httpx.AsyncClient, run_id: str
    ) -> dict[str, Any]:
        get_response = await self.call_api_async(
            client=client, url="/map/run/data", method="GET", params={"run_id": run_id}
        )
        if get_response.status_code != 200:
            raise Exception(f"Failed to get data for run {run_id}: {get_response.text}")
        return get_response.json().get("data", {}) or {}
