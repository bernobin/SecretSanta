from typing import TypedDict

from api.src.models import Participant, GiftAssignment
from api.src.repositories import UserRepository


class RevealedMatching(TypedDict):
    giver: str
    receiver: str


class AnonymizedMatching(TypedDict):
    giver_emoji: str
    receiver: str


class MatchingPresenter:
    """Convert saved assignments into readable matching results."""

    def __init__(
        self,
        users_repo: UserRepository,
    ) -> None:
        self._users = users_repo

    async def present(
        self,
        participants: list[Participant],
        assignments: list[GiftAssignment],
    ) -> list[RevealedMatching]:
        participant_by_id = {
            participant.participant_id: participant
            for participant in participants
        }

        if len(assignments) != len(participants):
            raise ValueError(
                "The session has an incomplete matching."
            )

        matchings: list[RevealedMatching] = []

        for assignment in assignments:
            giver = participant_by_id.get(
                assignment.giver_participant_id
            )
            receiver = participant_by_id.get(
                assignment.recipient_participant_id
            )

            if giver is None or receiver is None:
                raise ValueError(
                    "Matching references a missing participant."
                )

            matchings.append({
                "giver": await self._display_name(giver),
                "receiver": await self._display_name(receiver),
            })

        return matchings

    async def _display_name(
        self,
        participant: Participant,
    ) -> str:
        user = await self._users.get_by_id(participant.user_id)

        if user is None:
            return str(participant.user_id)

        return (
            user.username
            or user.first_name
            or str(participant.user_id)
        )

    async def present_anonymized(
        self,
        participants: list[Participant],
        assignments: list[GiftAssignment],
    ) -> list[AnonymizedMatching]:
        participant_by_id = {
            participant.participant_id: participant
            for participant in participants
        }

        if len(assignments) != len(participants):
            raise ValueError(
                "The session has an incomplete matching."
            )

        matchings: list[AnonymizedMatching] = []

        for assignment in assignments:
            giver = participant_by_id.get(
                assignment.giver_participant_id
            )
            receiver = participant_by_id.get(
                assignment.recipient_participant_id
            )

            if giver is None or receiver is None:
                raise ValueError(
                    "Matching references a missing participant."
                )

            matchings.append({
                "giver_emoji": giver.emoji,
                "receiver": await self._display_name(receiver),
            })

        return matchings