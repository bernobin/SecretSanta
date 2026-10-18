from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Users


class UserRepository:
    """Persistence operations for users."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: int) -> Users | None:
        """Retrieve a user by primary key."""
        return await self._db.get(Users, user_id)

    async def get_by_chatid(self, chatid: int) -> Users | None:
        """Retrieve a user by their external chat ID."""
        statement = select(Users).where(Users.chatid == chatid)
        result = await self._db.scalars(statement)
        return result.first()

    async def create(
        self,
        chatid: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Users:
        """Insert a user."""
        user = Users(
            chatid=chatid,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        self._db.add(user)
        await self._db.flush()

        return user
