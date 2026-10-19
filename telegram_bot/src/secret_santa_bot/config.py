
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str


def load_settings(environ: Mapping[str, str]) -> Settings:
    token = environ["TELEGRAM_BOT_TOKEN"]

    if not token.strip():
        raise ValueError("TELEGRAM_BOT_TOKEN must not be empty")

    return Settings(telegram_bot_token=token)
