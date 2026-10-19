
import os

from telegram.ext import Application

from secret_santa_bot.config import load_settings


def main() -> None:
    settings = load_settings(os.environ)

    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .build()
    )

    application.run_polling()


if __name__ == "__main__":
    main()
