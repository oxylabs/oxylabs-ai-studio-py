import asyncio
import time
from typing import Any

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
        search_keywords: list[str] | None = None,
        user_prompt: str | None = None,
        max_crawl_depth: int = 1,
        limit: int = 25,
        geo_location: str | None = None,
        render_javascript: bool = False,
        include_sitemap: bool = True,
        max_credits: int | None = None,
        allow_subdomains: bool = False,
        allow_external_domains: bool = False,
    ) -> AiMapJob:
        body = {
            "url": url,
            "search_keywords": (search_keywords or []),
            "user_prompt": user_prompt,
            "max_crawl_depth": max_crawl_depth,
            "limit": limit,
            "geo_location": geo_location,
            "render_javascript": render_javascript,
            "include_sitemap": include_sitemap,
            "max_credits": max_credits,
            "allow_subdomains": allow_subdomains,
            "allow_external_domains": allow_external_domains,
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
                        url="/map/run/data",
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
                        message=resp_body.get("error_code", None),
                        data=resp_body.get("data", {}) or {},
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

    async def map_async(
        self,
        url: str,
        search_keywords: list[str] | None = None,
        user_prompt: str | None = None,
        max_crawl_depth: int = 1,
        limit: int = 25,
        geo_location: str | None = None,
        render_javascript: bool = False,
        include_sitemap: bool = True,
        max_credits: int | None = None,
        allow_subdomains: bool = False,
        allow_external_domains: bool = False,
    ) -> AiMapJob:
        body = {
            "url": url,
            "search_keywords": (search_keywords or []),
            "user_prompt": user_prompt,
            "max_crawl_depth": max_crawl_depth,
            "limit": limit,
            "geo_location": geo_location,
            "render_javascript": render_javascript,
            "include_sitemap": include_sitemap,
            "max_credits": max_credits,
            "allow_subdomains": allow_subdomains,
            "allow_external_domains": allow_external_domains,
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
                            url="/map/run/data",
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
                        return AiMapJob(
                            run_id=run_id,
                            message=resp_body.get("error_code", None),
                            data=resp_body.get("data", {}) or {},
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
