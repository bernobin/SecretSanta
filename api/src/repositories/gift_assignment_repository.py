from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.models import GiftAssignment


class GiftAssignmentRepository:
    """Persistence operations for gift assignments."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_for_giver(
        self,
        session_id: int,
        giver_participant_id: int,
    ) -> GiftAssignment | None:
        """Retrieve the assignment belonging to a giver."""
        statement = select(GiftAssignment).where(
            GiftAssignment.giver_session_id == session_id,
            GiftAssignment.giver_participant_id == giver_participant_id,
        )
        result = await self._db.scalars(statement)
        return result.first()

    async def get_by_session(
        self,
        session_id: int,
    ) -> list[GiftAssignment]:
        """Retrieve all assignments for a session."""
        statement = (
            select(GiftAssignment)
            .where(
                GiftAssignment.giver_session_id == session_id
            )
            .order_by(GiftAssignment.assignment_id)
        )
        result = await self._db.scalars(statement)
        return list(result.all())

    async def create(
        self,
        session_id: int,
        giver_participant_id: int,
        recipient_participant_id: int,
    ) -> GiftAssignment:
        """Persist an assignment between two participants."""
        if giver_participant_id == recipient_participant_id:
            raise ValueError(
                "A participant cannot be assigned to themselves."
            )

        assignment = GiftAssignment(
            giver_session_id=session_id,
            giver_participant_id=giver_participant_id,
            recipient_session_id=session_id,
            recipient_participant_id=recipient_participant_id,
        )

        self._db.add(assignment)
        await self._db.flush()
        return assignment