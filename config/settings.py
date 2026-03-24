# config/settings.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    QDRANT_HOST    : str = "localhost"
    QDRANT_PORT    : int = 6333
    QDRANT_API_KEY : str = ""
    OPENAI_API_KEY : str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()