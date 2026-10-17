from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.models import Participant


class ParticipantRepository:
    """Persistence operations for session participants."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_user(
        self,
        session_id: int,
        user_id: int,
    ) -> Participant | None:
        """Retrieve a user's participation in a particular session."""
        statement = select(Participant).where(
            Participant.session_id == session_id,
            Participant.user_id == user_id,
        )
        result = await self._db.scalars(statement)
        return result.first()

    async def get_by_session(
        self,
        session_id: int,
    ) -> list[Participant]:
        """Retrieve all participants in signup order."""
        statement = (
            select(Participant)
            .where(Participant.session_id == session_id)
            .order_by(Participant.signed_up_at)
        )
        result = await self._db.scalars(statement)
        return list(result.all())

    async def create(
        self,
        session_id: int,
        user_id: int,
        emoji: str,
    ) -> Participant:
        """Insert a participant record."""
        participant = Participant(
            session_id=session_id,
            user_id=user_id,
            emoji=emoji,
        )
        self._db.add(participant)
        await self._db.flush()
        return participant

    async def update_emoji(
        self,
        session_id: int,
        user_id: int,
        emoji: str,
    ) -> Participant:
        """Update a participant's emoji."""
        participant = await self.get_by_user(session_id, user_id)

        if participant is None:
            raise ValueError("Participant does not exist.")

        participant.emoji = emoji
        await self._db.flush()
        return participant

    async def delete(
        self,
        session_id: int,
        user_id: int,
    ) -> None:
        """Delete a user's participation record."""
        participant = await self.get_by_user(session_id, user_id)

        if participant is None:
            raise ValueError("Participant does not exist.")

        await self._db.delete(participant)
        await self._db.flush()