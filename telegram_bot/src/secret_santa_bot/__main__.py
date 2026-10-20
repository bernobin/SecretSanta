import os

from secret_santa_bot.api_client import create_api_client
from secret_santa_bot.config import load_settings
from secret_santa_bot.telegram_app import create_telegram_application


def main() -> None:
    settings = load_settings(os.environ)
    api_client = create_api_client(settings)

    telegram_runtime = create_telegram_application(
        telegram_bot_token=settings.telegram_bot_token,
        api_client=api_client,
    )

    telegram_runtime.run_polling()


if __name__ == "__main__":
    main()