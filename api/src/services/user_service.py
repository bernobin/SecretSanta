from src.models import Users
from src.repositories.user_repository import UserRepository


class UserService:
    """Application operations for users."""

    def __init__(self, users_repo: UserRepository) -> None:
        self._users = users_repo

    async def create_user(
        self,
        *,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        chatid: int,
    ) -> Users:
        """Create a user with an optional external identifier."""
        return await self._users.create(
            chatid=chatid,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

    async def get_user(self, userid: int) -> Users:
        """Retrieve a user by internal database ID."""
        user = await self._users.get_by_id(userid)

        if user is None:
            raise ValueError(f"User ID {userid} does not exist.")

        return user

    async def get_by_chatid(self, chatid: int) -> Users | None:
        """Retrieve a user by their external Telegram ID."""
        return await self._users.get_by_chatid(chatid)

    async def get_or_create_telegram_user(
        self,
        *,
        chatid: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> Users:
        """Find a Telegram user or register them."""
        user = await self._users.get_by_chatid(chatid)

        if user is None:
            return await self._users.create(
                chatid=chatid,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )

        # Keep profile details up to date.
        user.username = username
        user.first_name = first_name
        user.last_name = last_name

        return user
