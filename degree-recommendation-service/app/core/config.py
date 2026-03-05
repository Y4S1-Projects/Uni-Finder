# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Degree Recommendation Service"
    ENV: str = "development"

    # Server
    PORT: int = 5001

    # Data
    DATA_DIR: str = "data"

    # ML
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    # API
    MAX_RECOMMENDATIONS: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
