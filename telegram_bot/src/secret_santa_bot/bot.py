import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from secret_santa_bot.messages import get_welcome_message

logger = logging.getLogger(__name__)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Respond to the /start command."""
    del context

    if update.effective_message is None:
        return

    await update.effective_message.reply_text(get_welcome_message())


def main() -> None:
    """Configure and start the Telegram bot."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("The TELEGRAM_BOT_TOKEN environment variable is required.")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))

    logger.info("Starting Secret Santa Telegram bot.")
    application.run_polling()


if __name__ == "__main__":
    main()
