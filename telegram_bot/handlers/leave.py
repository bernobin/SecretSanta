
from telegram import Update
from telegram.ext import ContextTypes

from services.api_client import APIError
from services.common import (
    get_api, get_session_name, report_api_error,
    require_registered_user,
)


async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await require_registered_user(update, context)
    if not user:
        return

    name = get_session_name(context)
    if not name:
        await update.effective_message.reply_text(
            "Usage: /leave <sessionname>\nExample: /leave office2026"
        )
        return

    try:
        await get_api(context).leave(name, user["userid"])
    except APIError as error:
        await report_api_error(update, error)
        return

    await update.effective_message.reply_text(
        f"You have left '{name}'."
    )
