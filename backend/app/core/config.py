from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.2-11b-vision-preview"
    MAX_FILE_SIZE_MB: int = 10
    MAX_IMAGE_EDGE_PX: int = 1536


settings = Settings()
