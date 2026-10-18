from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Database:
    def __init__(self, database_url: str) -> None:
        self.engine = create_async_engine(database_url)

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    def transaction(
        self,
    ) -> AbstractAsyncContextManager[AsyncSession]:
        """Return a context manager for one async transaction."""
        return self.session_factory.begin()

    async def close(self) -> None:
        """Dispose of the engine and its connection pool."""
        await self.engine.dispose()
