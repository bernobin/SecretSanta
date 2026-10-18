from collections.abc import AsyncIterator

from fastapi import Request

from src.classes.database import Database

import os
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.sessions_service import SessionService
from src.services.user_service import UserService
from src.services.matching_generator import MatchingGenerator
from src.services.matching_presenter import MatchingPresenter

from src.repositories.user_repository import UserRepository
from src.repositories.session_repository import SessionRepository
from src.repositories.participant_repository import ParticipantRepository
from src.repositories.gift_assignment_repository import GiftAssignmentRepository


@dataclass
class ApplicationServices:
    users: UserService
    sessions: SessionService


def create_services(db: AsyncSession) -> ApplicationServices:
    emoji_pool = tuple(
        emoji.strip()
        for emoji in os.environ["SECRET_SANTA_EMOJIS"].split(",")
        if emoji.strip()
    )

    users_repo = UserRepository(db)
    sessions_repo = SessionRepository(db)
    participants_repo = ParticipantRepository(db)
    assignments_repo = GiftAssignmentRepository(db)

    matching_generator = MatchingGenerator()
    matching_presenter = MatchingPresenter(users_repo)

    users_service = UserService(users_repo)

    sessions_service = SessionService(
        sessions_repo,
        participants_repo,
        users_repo,
        assignments_repo,
        emoji_pool,
        matching_generator,
        matching_presenter,
    )

    return ApplicationServices(
        users=users_service,
        sessions=sessions_service,
    )


async def get_services(
    request: Request,
) -> AsyncIterator[ApplicationServices]:
    database: Database = request.app.state.database

    async with database.transaction() as db:
        services = create_services(db)
        yield services
