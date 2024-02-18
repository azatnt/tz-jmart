from functools import lru_cache
from typing import Optional, Any, Dict
from pydantic import validator, BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "JMART"

    DB_SERVER: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_PORT: int = 5432
    DATABASE_URI: Optional[str] = None
    DB_SCHEMA: str = "public"
    DB_POOL_SIZE: int = 5
    ECHO: bool = False
    DB_MAX_OVERFLOW: int = 10
    SECRET_KEY: str = None
    ALGORITHM: str = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = None
    SUPERUSER_USERNAME: str
    SUPERUSER_PASSWORD: str
    SUPERUSER_EMAIL: str

    USE_TZ: bool = True
    TZ: str = "Asia/Almaty"

    SHOW_DOCS_ENVIRONMENT: list = ("local", "dev")

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return (
            f"postgresql+asyncpg://"
            f"{values['DB_USER']}:"
            f"{values['DB_PASSWORD']}@"
            f"{values['DB_SERVER']}/"
            f"{values['DB_NAME']}"
        )

    class Config:
        case_sensitive = True
        env_file = "/Users/azatamanzol/PycharmProjects/tz-jmart/.env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
