from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # === MySQL ===
    API_MYSQL_HOSTNAME: str = Field(..., validation_alias="API_MYSQL_HOSTNAME")
    API_MYSQL_PORT: str = Field(..., validation_alias="API_MYSQL_PORT")
    API_MYSQL_USERNAME: str = Field(..., validation_alias="API_MYSQL_USERNAME")
    API_MYSQL_PASSWORD: str = Field(..., validation_alias="API_MYSQL_PASSWORD")

    # === JWT ===
    SECRET_KEY_JWT: str = Field(..., validation_alias="SECRET_KEY_JWT")
    ALGORITHM_JWT: str = Field(..., validation_alias="ALGORITHM_JWT")

    # === SMTP / Email ===
    SMTP_HOST: str = Field("smtp.gmail.com", validation_alias="SMTP_HOST")
    SMTP_PORT: int = Field(587, validation_alias="SMTP_PORT")
    SMTP_USER: str = Field(..., validation_alias="SMTP_USER")
    SMTP_PASSWORD: str = Field(..., validation_alias="SMTP_PASSWORD")
    SMTP_FROM: str = Field(..., validation_alias="SMTP_FROM")
    SMTP_SENDER_NAME: str = Field("PLAX Notifiche", validation_alias="SMTP_SENDER_NAME")
    SMTP_TLS: bool = Field(True, validation_alias="SMTP_TLS")

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings():
    return Settings()
