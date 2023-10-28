from logging import config as logging_config
from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = Path(__file__).parent.parent
ENV_PATH = BASE_DIR.parent / ".env"


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="jwt_", env_file=ENV_PATH, env_file_encoding="utf-8")

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    token_type: str = "Bearer"


class ApplicationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="app_", env_file=ENV_PATH, env_file_encoding="utf-8")

    host: str = "127.0.0.1"
    port: int = 8000
    title: str = "API"
    version: str = "0.1.0"
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    storage_directory: Path = BASE_DIR / "storage"

    def model_post_init(self, __context) -> None:
        if not self.storage_directory.exists():
            self.storage_directory.mkdir(parents=True, exist_ok=True)


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="database_", env_file=ENV_PATH, env_file_encoding="utf-8")

    dsn: PostgresDsn
    echo: bool = False


class Settings(BaseSettings):
    app: ApplicationSettings = ApplicationSettings()
    jwt: JWTSettings = JWTSettings()
    db: DatabaseSettings = DatabaseSettings()


settings = Settings()
