import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Dialogs"
    PROJECT_VERSION: str = "0.0.1"
    REDIS_DIALOG_HOST: str
    REDIS_DIALOG_LOGIN: str
    REDIS_DIALOG_PORT: int
    REDIS_DIALOG_PASSWORD: str
    REDIS_DIALOG_DB: int

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )


settings = Settings()
