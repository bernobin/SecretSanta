
from telegram import Update
from telegram.ext import ContextTypes

from services.api_client import APIError
from services.common import (
    get_api, get_session_name, report_api_error,
    require_registered_user,
)


async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await require_registered_user(update, context)
    if not user:
        return

    name = get_session_name(context)
    if not name:
        await update.effective_message.reply_text(
            "Usage: /create <sessionname>\nExample: /create office2026"
        )
        return

    try:
        session = await get_api(context).create_session(
            name, user["userid"]
        )
    except APIError as error:
        await report_api_error(update, error)
        return

    await update.effective_message.reply_text(
        f"🎁 Session '{session.get('sessionname', name)}' created!\n"
        "You are the administrator.\n\n"
        f"Join: /join {name}\n"
        f"Status: /status {name}\n"
        f"Start: /begin {name}"
    )
