
from telegram import Update
from telegram.ext import ContextTypes

from services.api_client import APIError
from services.common import get_api, report_api_error


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    message = update.effective_message

    if telegram_user is None or message is None:
        return

    client = get_api(context)

    # Check whether the Telegram user is already registered.
    try:
        existing_user = await client.get_user_by_chat_id(
            telegram_user.id
        )
    except APIError as error:
        await report_api_error(update, error)
        return

    if existing_user is not None:
        await message.reply_text(
            "🎅 Welcome back to Secret Santa!\n\n"
            "You're already registered.\n"
            "Use /help to see the available commands."
        )
        return

    # Only create a user if no matching record exists.
    try:
        user = await client.create_user(telegram_user)
    except APIError as error:
        # Handle a possible race: another request might have registered
        # the user after our initial lookup. HTTP 409 is a conflict.
        if error.status_code == 409:
            try:
                existing_user = await client.get_user_by_chat_id(
                    telegram_user.id
                )
            except APIError as lookup_error:
                await report_api_error(update, lookup_error)
                return

            if existing_user is not None:
                await message.reply_text(
                    "🎅 Welcome back to Secret Santa!\n\n"
                    "You're already registered.\n"
                    "Use /help to see the available commands."
                )
                return

        await message.reply_text(
            "I couldn't register you with Secret Santa.\n"
            "Please send /start again to retry."
        )
        return

    if not isinstance(user, dict) or not user.get("userid"):
        await message.reply_text(
            "Registration returned an unexpected response.\n"
            "Please send /start again to retry."
        )
        return

    await message.reply_text(
        "🎅 Welcome to Secret Santa!\n\n"
        "You're registered and ready to go.\n"
        "Use /help to see the available commands."
    )
