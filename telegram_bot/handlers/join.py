
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ContextTypes

from services.api_client import APIError
from services.common import (
    get_api, get_session_name, report_api_error,
    require_registered_user,
)


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if not chat or chat.type != ChatType.PRIVATE:
        await update.effective_message.reply_text(
            "Please use this command in a private chat with me."
        )
        return

    user = await require_registered_user(update, context)
    if not user:
        return

    name = get_session_name(context)
    if not name:
        await update.effective_message.reply_text(
            "Usage: /join <sessionname>\nExample: /join office2026"
        )
        return

    try:
        participant = await get_api(context).join(name, user["userid"])
    except APIError as error:
        await report_api_error(update, error)
        return

    emoji = participant.get("emoji", "🎁")
    await update.effective_message.reply_text(
        f"You're in! Your session emoji is {emoji}"
    )
    