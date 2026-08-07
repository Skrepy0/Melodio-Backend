from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = (
    Path(__file__).resolve().parent.parent.parent
)  # 返回 /path/to/my-music-app


class Settings(BaseSettings):
    SECRET_KEY: str
    SIGNATURE_EXPIRE_SECONDS: int = 300

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / '.env'),
        extra='ignore',
        case_sensitive=True,
    )


settings = Settings()
