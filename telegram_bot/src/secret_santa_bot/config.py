
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    api_base_url: str


def load_settings(environ: Mapping[str, str]) -> Settings:
    token = environ["TELEGRAM_BOT_TOKEN"]
    api_base_url = environ["SECRET_SANTA_API_BASE_URL"]

    if not token.strip():
        raise ValueError("TELEGRAM_BOT_TOKEN must not be empty")

    if not api_base_url.strip():
        raise ValueError("SECRET_SANTA_API_BASE_URL must not be empty")

    return Settings(
        telegram_bot_token=token,
        api_base_url=api_base_url
    )
