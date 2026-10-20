from dataclasses import dataclass
from typing import Any

from telegram.ext import (
    Application,
    ContextTypes,
    ExtBot,
    JobQueue,
)

from secret_santa_bot.generated_client.secret_santa_api_client import Client


_TelegramApplication = Application[
    ExtBot[None],
    ContextTypes.DEFAULT_TYPE,
    dict[Any, Any],
    dict[Any, Any],
    dict[Any, Any],
    JobQueue[ContextTypes.DEFAULT_TYPE],
]


@dataclass(frozen=True)
class TelegramRuntime:
    _application: _TelegramApplication

    def run_polling(self) -> None:
        self._application.run_polling()


def create_telegram_application(
    telegram_bot_token: str,
    api_client: Client,
) -> TelegramRuntime:
    async def post_shutdown(
        _application: _TelegramApplication,
    ) -> None:
        await api_client.get_async_httpx_client().aclose()

    application = (
        Application.builder()
        .token(telegram_bot_token)
        .post_shutdown(  # pyright: ignore[reportUnknownMemberType]
            post_shutdown
        )
        .build()
    )

    application.bot_data["api_client"] = api_client

    return TelegramRuntime(application)