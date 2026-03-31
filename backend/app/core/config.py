from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "fnnas-media-hub"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'media.db')}"

    FN_NAS_HOST: Optional[str] = None
    FN_NAS_TOKEN: Optional[str] = None

    TMDB_API_KEY: Optional[str] = None
    DOUBAN_API_KEY: Optional[str] = None

    DOWNLOAD_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "downloads")
    TEMP_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "temp")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

os.makedirs(settings.DOWNLOAD_PATH, exist_ok=True)
os.makedirs(settings.TEMP_PATH, exist_ok=True)
