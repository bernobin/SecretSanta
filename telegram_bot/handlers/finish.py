
from telegram import Update
from telegram.ext import ContextTypes

from services.api_client import APIError
from services.common import (
    get_api, get_session_name, report_api_error,
    require_admin, require_registered_user,
)


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await require_registered_user(update, context)
    if not user:
        return

    name = get_session_name(context)
    if not name:
        await update.effective_message.reply_text(
            "Usage: /finish <sessionname>\nExample: /finish office2026"
        )
        return

    if await require_admin(update, context, name, user) is None:
        return

    try:
        session = await get_api(context).end_session(name)
    except APIError as error:
        await report_api_error(update, error)
        return

    await update.effective_message.reply_text(
        f"🏁 Session '{name}' finished.\n"
        f"Status: {session.get('status', 'finished')}"
    )
