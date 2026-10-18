
import logging

from telegram import Update
from telegram.ext import ContextTypes

from services.api_client import APIError
from services.common import (
    display_name, get_api, get_session_name,
    report_api_error, require_registered_user,
)

logger = logging.getLogger(__name__)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await require_registered_user(update, context)
    if not user:
        return

    name = get_session_name(context)
    if not name:
        await update.effective_message.reply_text(
            "Usage: /status <sessionname>\nExample: /status office2026"
        )
        return

    client = get_api(context)

    try:
        result = await client.get_session_status(name)
        session = result["session"]
        participants = await client.get_participants(name)

        lines = [
            f"🎁 Secret Santa: {session.get('sessionname', name)}",
            f"Status: {session.get('status', 'unknown')}",
            "",
            f"Participants ({len(participants)}):",
        ]

        for participant in participants:
            participant_user = await client.get_user(
                participant["user_id"]
            )
            lines.append(display_name(participant_user))

        if not participants:
            lines.append("No participants yet.")



        assignment_ids = result.get("assignments") or []

        if assignment_ids:
            lines.extend(["", "🎄 Assignments:"])

            for assignment_id in assignment_ids:
                giver = await client.get_giver(name, assignment_id)
                receiver = await client.get_receiver(name, assignment_id)

                giver_participant = await client.get_participant(
                    name, giver["participant_id"]
                )
                receiver_participant = await client.get_participant(
                    name, receiver["participant_id"]
                )

                giver_user = await client.get_user(
                    giver_participant["user_id"]
                )
                receiver_user = await client.get_user(
                    receiver_participant["user_id"]
                )

                lines.append(
                    f"{display_name(giver_user)} → "
                    f"{display_name(receiver_user)}"
                )
        else:
            lines.extend(["", "Assignments have not been drawn yet."])


        await update.effective_message.reply_text("\n".join(lines))

    except APIError as error:
        await report_api_error(update, error)
    except (KeyError, TypeError):
        logger.exception("Unexpected API response for session %s", name)
        await update.effective_message.reply_text(
            "The API returned an unexpected response while loading status."
        )
