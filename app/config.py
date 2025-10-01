import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Dialogs"
    PROJECT_VERSION: str = "0.2.1"
    REDIS_DIALOG_HOST: str
    REDIS_DIALOG_LOGIN: str
    REDIS_DIALOG_PORT: int
    REDIS_DIALOG_PASSWORD: str
    REDIS_DIALOG_DB: int
    DIALOG_UNREAD_MESSAGES_HOST: str
    DIALOG_UNREAD_MESSAGES_PORT: str
    DIALOG_UNREAD_ADD_URL: str
    DIALOG_UNREAD_GET_URL: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )


settings = Settings()
