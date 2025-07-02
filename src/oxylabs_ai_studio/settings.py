from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    OXYLABS_AI_STUDIO_API_KEY: str | None = None
    OXYLABS_AI_STUDIO_API_URL: str = "https://api-aistudio.oxylabs.io"


settings = Settings()
