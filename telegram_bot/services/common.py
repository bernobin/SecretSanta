
from telegram import Update
from telegram.ext import ContextTypes

from services.api_client import APIError, SecretSantaAPI


def get_api(context: ContextTypes.DEFAULT_TYPE) -> SecretSantaAPI:
    return context.application.bot_data["api"]


def get_session_name(context: ContextTypes.DEFAULT_TYPE) -> str | None:
    if len(context.args) != 1:
        return None

    name = context.args[0].strip()
    return name or None


def display_name(user: dict) -> str:
    if user.get("username"):
        return f"@{user['username']}"

    full_name = " ".join(
        value
        for value in (user.get("first_name"), user.get("last_name"))
        if value
    )
    return full_name or f"User {user.get('userid', '?')}"


async def report_api_error(update: Update, error: APIError):
    message = update.effective_message
    if message is None:
        return


async def report_api_error(update: Update, error: APIError):
    message = update.effective_message
    if message is None:
        return

    if error.status_code == 0:
        text = "The Secret Santa API is unavailable. Please try again later."
    else:
        text = error.detail or "The request failed. Please try again."

    await message.reply_text(text)


async def require_registered_user(update: Update, context):
    telegram_user = update.effective_user
    message = update.effective_message

    if telegram_user is None or message is None:
        return None

    try:
        user = await get_api(context).get_user_by_chat_id(
            telegram_user.id
        )
    except APIError as error:
        await report_api_error(update, error)
        return None

    if user is None:
        await message.reply_text(
            "You are not registered yet. Please send /start first."
        )
        return None

    return user


async def require_admin(update: Update, context, session_name, user):
    try:
        result = await get_api(context).get_session_status(session_name)
    except APIError as error:
        await report_api_error(update, error)
        return None

    session = result.get("session", {})
    if session.get("admin_userid") != user.get("userid"):
        await update.effective_message.reply_text(
            "Only the administrator of this session can do that."
        )
        return None

    return result
