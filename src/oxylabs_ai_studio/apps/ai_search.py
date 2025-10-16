import asyncio
import time

from pydantic import BaseModel

from oxylabs_ai_studio.client import OxyStudioAIClient
from oxylabs_ai_studio.logger import get_logger

SEARCH_TIMEOUT_SECONDS = 60 * 3
POLL_INTERVAL_SECONDS = 5
POLL_MAX_ATTEMPTS = SEARCH_TIMEOUT_SECONDS // POLL_INTERVAL_SECONDS

logger = get_logger(__name__)


class SearchResult(BaseModel):
    url: str
    title: str
    description: str
    content: str | None


class AiSearchJob(BaseModel):
    run_id: str
    message: str | None = None
    data: list[SearchResult] | None


class AiSearch(OxyStudioAIClient):
    """AI Search app."""

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)

    def search(
        self,
        query: str,
        limit: int = 10,
        render_javascript: bool = False,
        return_content: bool = True,
        geo_location: str | None = None,
    ) -> AiSearchJob:
        if not query:
            raise ValueError("query is required")

        body = {
            "query": query,
            "limit": limit,
            "render_html": render_javascript,
            "return_content": return_content,
            "geo_location": geo_location,
        }
        client = self.get_client()
        create_response = self.call_api(
            client=client, url="/search/run", method="POST", body=body
        )
        status_code = create_response.status_code
        if status_code != 200:
            raise Exception(f"Failed to create search job: `{create_response.text}`")
        resp_body = create_response.json()
        run_id = resp_body["run_id"]
        try:
            for _ in range(POLL_MAX_ATTEMPTS):
                try:
                    get_response = self.call_api(
                        client=client,
                        url="/search/run/data",
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
                if resp_body["status"] == "completed":
                    return AiSearchJob(
                        run_id=run_id,
                        message=resp_body.get("message", None),
                        data=resp_body["data"],
                    )
                if resp_body["status"] == "failed":
                    return AiSearchJob(
                        run_id=run_id,
                        message=resp_body.get("error_code", None),
                        data=None,
                    )
                time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("[Cancelled] Request was cancelled by user.")
            raise KeyboardInterrupt from None
        except Exception as e:
            raise e
        raise TimeoutError(f"Failed to search {query=}")

    async def search_async(
        self,
        query: str,
        limit: int = 10,
        render_javascript: bool = False,
        return_content: bool = True,
        geo_location: str | None = None,
    ) -> AiSearchJob:
        """Async version of search."""
        if not query:
            raise ValueError("query is required")

        body = {
            "query": query,
            "limit": limit,
            "render_html": render_javascript,
            "return_content": return_content,
            "geo_location": geo_location,
        }
        async with self.async_client() as client:
            create_response = await self.call_api_async(
                client=client, url="/search/run", method="POST", body=body
            )

            resp_body = create_response.json()
            run_id = resp_body["run_id"]
            try:
                for _ in range(POLL_MAX_ATTEMPTS):
                    try:
                        get_response = await self.call_api_async(
                            client=client,
                            url="/search/run/data",
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
                    if resp_body["status"] == "completed":
                        return AiSearchJob(
                            run_id=run_id,
                            message=resp_body.get("message"),
                            data=resp_body["data"],
                        )
                    if resp_body["status"] == "failed":
                        logger.error("[search_async] job failed run_id=%s", run_id)
                        return AiSearchJob(
                            run_id=run_id,
                            message=resp_body.get("error_code", None),
                            data=None,
                        )
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                logger.info("[Cancelled] Request was cancelled by user.")
                raise KeyboardInterrupt from None
            except Exception as e:
                raise e
            raise TimeoutError(f"Failed to search {query=}")
