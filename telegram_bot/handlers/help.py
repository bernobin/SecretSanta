
from telegram import Update
from telegram.ext import ContextTypes


async def help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.effective_message.reply_text(
        "🎁 Secret Santa commands\n\n"
        "/start — Register with Secret Santa\n"
        "/help — Show available commands\n"
        "/create <sessionname> — Create a session\n"
        "/status <sessionname> — Show participants and assignments\n"
        "/join <sessionname> — Join a session\n"
        "/leave <sessionname> — Leave a session\n"
        "/begin <sessionname> — Start the session (admin only)\n"
        "/finish <sessionname> — Finish the session (admin only)\n\n"
        "Example: /create office2026"
    )
