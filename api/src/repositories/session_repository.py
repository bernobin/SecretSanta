from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.models import Sessions, Users


class SessionRepository:
    """Persistence operations for Secret Santa sessions."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, session_id: int) -> Sessions | None:
        """Retrieve a session by primary key."""
        return await self._db.get(Sessions, session_id)

    async def get_by_name(self, sessionname: str) -> Sessions | None:
        """Retrieve a session by its unique name."""
        statement = select(Sessions).where(
            Sessions.sessionname == sessionname
        )
        result = await self._db.scalars(statement)
        return result.first()

    async def get_by_name_for_update(
        self,
        sessionname: str,
    ) -> Sessions | None:
        """Retrieve and lock a session row for a lifecycle operation."""
        statement = (
            select(Sessions)
            .where(Sessions.sessionname == sessionname)
            .with_for_update()
        )
        result = await self._db.scalars(statement)
        return result.first()

    async def create(
        self,
        sessionname: str,
        admin_userid: int,
        seed: str | None = None,
    ) -> Sessions:
        """Insert a new session."""
        session = Sessions(
            sessionname=sessionname,
            admin_userid=admin_userid,
            seed=seed,
        )
        self._db.add(session)
        await self._db.flush()
        return session

    async def update(
        self,
        session_id: int,
        *,
        sessionname: str | None = None,
        admin_userid: int | None = None,
        seed: str | None = None,
        status: str | None = None,
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
    ) -> Sessions:
        """Update persisted session fields."""
        session = await self._db.get(Sessions, session_id)

        if session is None:
            raise ValueError("Session does not exist.")

        if status is not None and status not in {
            "new", "started", "finished",
        }:
            raise ValueError("Invalid session status.")

        if (
            admin_userid is not None
            and await self._db.get(Users, admin_userid) is None
        ):
            raise ValueError("Administrator does not exist.")

        if sessionname is not None:
            session.sessionname = sessionname

        if admin_userid is not None:
            session.admin_userid = admin_userid

        if seed is not None:
            session.seed = seed

        if status is not None:
            session.status = status

        if started_at is not None:
            session.started_at = started_at

        if ended_at is not None:
            session.ended_at = ended_at

        await self._db.flush()
        return session