import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from services.api_client import SecretSantaAPI
from handlers.start import start
from handlers.help import help_command
from handlers.create import create
from handlers.status import status
from handlers.join import join
from handlers.leave import leave
from handlers.begin import begin
from handlers.finish import finish

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


async def post_init(application: Application):
    application.bot_data["api"] = SecretSantaAPI(
        os.getenv("API_BASE_URL", "http://api:8000")
    )


async def post_shutdown(application: Application):
    client = application.bot_data.get("api")
    if client:
        await client.close()


async def on_error(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.error("Unhandled Telegram bot error", exc_info=context.error)


def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]

    application = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    commands = [
        ("start", start),
        ("help", help_command),
        ("create", create),
        ("status", status),
        ("join", join),
        ("leave", leave),
        ("begin", begin),
        ("finish", finish),
    ]

    for command, handler in commands:
        application.add_handler(CommandHandler(command, handler))

    application.add_error_handler(on_error)

    logger.info("Starting Secret Santa Telegram bot")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
