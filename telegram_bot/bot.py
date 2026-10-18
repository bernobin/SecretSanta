
import logging
import os
from urllib.parse import quote

import httpx
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
API_BASE_URL = os.getenv(
    "API_BASE_URL", "http://api:8000"
).rstrip("/")

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO"),
)
logger = logging.getLogger(__name__)


async def api_request(method: str, path: str, **kwargs):
    async with httpx.AsyncClient(
        base_url=API_BASE_URL,
        timeout=15,
    ) as client:
        response = await client.request(method, path, **kwargs)

    if response.is_error:
        raise RuntimeError(
            f"API returned HTTP {response.status_code}: "
            f"{response.text}"
        )

    if response.status_code == 204 or not response.content:
        return None

    return response.json()


async def say(update: Update, text: str):
    if update.effective_message:
        await update.effective_message.reply_text(text)


async def find_user_by_chatid(chatid: int) -> dict | None:
    result = await api_request(
        "GET",
        "/users",
        params={"$filter": f"chatid eq {chatid}"},
    )

    if not result:
        return None

    if len(result) > 1:
        raise RuntimeError(
            f"Multiple API users found for Telegram ID {chatid}. "
            "Ensure chatid is unique in the database."
        )

    return result[0]


async def get_current_user(update: Update) -> dict | None:
    telegram_user = update.effective_user
    if telegram_user is None:
        return None

    return await find_user_by_chatid(telegram_user.id)


async def require_user(update: Update) -> dict | None:
    try:
        user = await get_current_user(update)
    except Exception:
        logger.exception("Could not look up Telegram user")
        await say(update, "Sorry, I couldn't contact the API. Try again.")
        return None

    if user is None:
        await say(
            update,
            "You aren't registered yet. Send /register first.",
        )

    return user


async def require_admin(
    update: Update,
    sessionname: str,
    user: dict,
) -> bool:
    session = await api_request(
        "GET",
        f"/sessions/{quote(sessionname, safe='')}",
    )

    if session["session"]["admin_userid"] != user["userid"]:
        await say(update, "Only this session's admin can do that.")
        return False

    return True


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await say(
        update,
        "🎅 Welcome to Secret Santa!\n\n"
        "Available commands:\n"
        "/register — register or link your Telegram account\n"
        "/me — show your API user details\n"
        "/newsession NAME [SEED] — create a session\n"
        "/join NAME — join a session\n"
        "/leave NAME — leave a session\n"
        "/status NAME — view session status and participants\n"
        "/draw NAME — start the draw (admin only)\n"
        "/finish NAME — end and reveal the draw (admin only)\n"
        "/help — show this message",
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await start(update, context)


async def register(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    telegram_user = update.effective_user
    if telegram_user is None:
        return

    try:
        user = await find_user_by_chatid(telegram_user.id)

        if user is not None:
            await say(
                update,
                "✅ You're already registered!\n"
                f"API user ID: {user['userid']}",
            )
            return

        user = await api_request(
            "POST",
            "/users",
            json={
                "chatid": telegram_user.id,
                "username": telegram_user.username,
                "first_name": telegram_user.first_name,
                "last_name": telegram_user.last_name,
            },
        )

        await say(
            update,
            "🎉 Registration successful!\n"
            f"API user ID: {user['userid']}",
        )

    except Exception:
        logger.exception("Registration failed")
        await say(
            update,
            "Registration failed. Please try again later.",
        )


async def me(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = await require_user(update)
    if user is None:
        return

    await say(
        update,
        f"User ID: {user['userid']}\n"
        f"Username: @{user['username']}"
        if user.get("username")
        else f"User ID: {user['userid']}\nNo username set.",
    )


async def new_session(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = await require_user(update)
    if user is None:
        return

    if not 1 <= len(context.args) <= 2:
        await say(update, "Usage: /newsession NAME [SEED]")
        return

    name = context.args[0]
    seed = context.args[1] if len(context.args) == 2 else None

    try:
        result = await api_request(
            "POST",
            "/sessions",
            json={
                "sessionname": name,
                "admin_userid": user["userid"],
                "seed": seed,
            },
        )

        await say(
            update,
            f"🎄 Session '{result['sessionname']}' created!\n"
            "You're the session admin.\n\n"
            f"Participants can join with /join {name}\n"
            f"Check progress with /status {name}",
        )
    except Exception:
        logger.exception("Session creation failed")
        await say(
            update,
            "Could not create the session. Check its name and try again.",
        )


async def join_session(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = await require_user(update)
    if user is None:
        return

    if len(context.args) != 1:
        await say(update, "Usage: /join NAME")
        return

    name = context.args[0]

    try:
        result = await api_request(
            "POST",
            f"/sessions/{quote(name, safe='')}"
            f"/participants/{user['userid']}",
        )

        await say(
            update,
            f"🎁 You've joined '{name}'!\n"
            f"Your participant emoji: {result['emoji']}",
        )
    except Exception:
        logger.exception("Session signup failed")
        await say(
            update,
            "Could not join the session. Check the session name "
            "and whether signups are allowed.",
        )


async def leave_session(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = await require_user(update)
    if user is None:
        return

    if len(context.args) != 1:
        await say(update, "Usage: /leave NAME")
        return

    name = context.args[0]

    try:
        await api_request(
            "DELETE",
            f"/sessions/{quote(name, safe='')}"
            f"/participants/{user['userid']}",
        )
        await say(update, f"You've left '{name}'.")
    except Exception:
        logger.exception("Session signoff failed")
        await say(update, "Could not leave the session.")


async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if len(context.args) != 1:
        await say(update, "Usage: /status NAME")
        return

    name = context.args[0]

    try:
        result = await api_request(
            "GET",
            f"/sessions/{quote(name, safe='')}",
        )
        session = result["session"]
        participants = result["participants"]

        lines = [
            f"🎄 Session: {session['sessionname']}",
            f"Status: {session['status']}",
            f"Participants ({len(participants)}):",
        ]

        for participant in participants:
            username = participant.get("username")
            display_name = (
                f"@{username}"
                if username
                else f"User {participant['user_id']}"
            )
            lines.append(f"{participant['emoji']} {display_name}")

        if not participants:
            lines.append("No participants yet.")

        await say(update, "\n".join(lines))
    except Exception:
        logger.exception("Session status lookup failed")
        await say(update, "Could not retrieve the session status.")


async def draw(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = await require_user(update)
    if user is None:
        return

    if len(context.args) != 1:
        await say(update, "Usage: /draw NAME")
        return

    name = context.args[0]

    try:
        if not await require_admin(update, name, user):
            return

        result = await api_request(
            "POST",
            f"/sessions/{quote(name, safe='')}/start",
        )

        await say(
            update,
            f"🎉 The draw for '{name}' has started!\n"
            f"{len(result['matchings'])} anonymized matchings generated.",
        )
    except Exception:
        logger.exception("Starting draw failed")
        await say(
            update,
            "Could not start the draw. Check the session status "
            "and participant count.",
        )


async def finish(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = await require_user(update)
    if user is None:
        return

    if len(context.args) != 1:
        await say(update, "Usage: /finish NAME")
        return

    # Revealed matchings must not be posted to a group chat.
    if (
        update.effective_chat is None
        or update.effective_chat.type != ChatType.PRIVATE
    ):
        await say(
            update,
            "For privacy, use /finish in a private chat with the bot.",
        )
        return

    name = context.args[0]

    try:
        if not await require_admin(update, name, user):
            return

        if not await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ Ending '{name}' will reveal all matchings.",
        ):
            return

        result = await api_request(
            "POST",
            f"/sessions/{quote(name, safe='')}/end",
        )

        lines = [f"🎁 Revealed results for '{name}':"]
        for matching in result["matchings"]:
            lines.append(
                f"{matching['giver']} → {matching['receiver']}"
            )

        await say(update, "\n".join(lines))
    except Exception:
        logger.exception("Ending session failed")
        await say(
            update,
            "Could not finish the session. Check its status and try again.",
        )


def main():
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    handlers = [
        ("start", start),
        ("help", help_command),
        ("register", register),
        ("me", me),
        ("newsession", new_session),
        ("join", join_session),
        ("leave", leave_session),
        ("status", status),
        ("draw", draw),
        ("finish", finish),
    ]

    for command, handler in handlers:
        application.add_handler(CommandHandler(command, handler))

    logger.info("Starting Telegram bot; API: %s", API_BASE_URL)
    application.run_polling()


if __name__ == "__main__":
    main()
