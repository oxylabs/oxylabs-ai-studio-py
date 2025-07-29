import httpx

from oxylabs_ai_studio.logger import get_logger
from oxylabs_ai_studio.settings import settings

logger = get_logger(__name__)


def is_api_key_valid(api_key: str) -> bool:
    try:
        response = httpx.get(
            f"{settings.OXYLABS_AI_STUDIO_API_URL}/status",
            headers={"x-api-key": api_key},
        )
        return response.status_code == 200
    except Exception:
        logger.exception("Error checking API key")
        return False
