from datetime import datetime, timezone
from typing import TypedDict
import secrets

from src.models import GiftAssignment, Participant, Sessions
from src.repositories.user_repository import UserRepository
from src.repositories.session_repository import SessionRepository
from src.repositories.gift_assignment_repository import GiftAssignmentRepository
from src.repositories.participant_repository import ParticipantRepository

from src.services.matching_generator import MatchingGenerator
from src.services.matching_presenter import MatchingPresenter


class SessionStatus(TypedDict):
    session: Sessions
    participants: list[int]
    assignments: list[int]


class SessionService:
    def __init__(
        self,
        sessions_repo: SessionRepository,
        participants_repo: ParticipantRepository,
        users_repo: UserRepository,
        assignments_repo: GiftAssignmentRepository,
        emoji_pool: tuple[str, ...],
        matching_generator: MatchingGenerator,
        matching_presenter: MatchingPresenter,
    ) -> None:
        self._sessions = sessions_repo
        self._participants = participants_repo
        self._users = users_repo
        self._assignments = assignments_repo
        self._emoji_pool = emoji_pool
        self._matching_generator = matching_generator
        self._matching_presenter = matching_presenter

        if not self._emoji_pool:
            raise ValueError("The emoji pool cannot be empty.")

    async def create_session(
        self,
        *,
        sessionname: str,
        admin_userid: int,
        seed: str | None = None,
    ) -> Sessions:
        """Create a new session owned by the requesting user."""
        sessionname = sessionname.strip()

        if not sessionname:
            raise ValueError("Session name cannot be empty.")

        if await self._sessions.get_by_name(sessionname) is not None:
            raise ValueError(f"Session '{sessionname}' already exists.")

        if await self._users.get_by_id(admin_userid) is None:
            raise ValueError("Administrator does not exist.")

        return await self._sessions.create(
            sessionname=sessionname,
            admin_userid=admin_userid,
            seed=seed,
        )

    async def get_session(
        self,
        sessionname: str,
        *,
        for_update: bool = False,
    ) -> Sessions:
        """Resolve a session by name, optionally locking its database row."""
        if for_update:
            session = await self._sessions.get_by_name_for_update(sessionname)
        else:
            session = await self._sessions.get_by_name(sessionname)

        if session is None:
            raise ValueError(f"Session '{sessionname}' does not exist.")

        return session

    async def signup(
        self,
        *,
        sessionname: str,
        user_id: int,
    ) -> Participant:
        """Register a user with a randomly selected, unique session emoji."""
        session = await self.get_session(
            sessionname,
            for_update=True,
        )

        if session.status != "new":
            raise ValueError("You can only join a session that has not started.")

        if await self._users.get_by_id(user_id) is None:
            raise ValueError("User does not exist.")

        if (
            await self._participants.get_by_user(
                session.sessionid,
                user_id,
            )
            is not None
        ):
            raise ValueError("You are already signed up.")

        participants = await self._participants.get_by_session(session.sessionid)
        used_emojis = {participant.emoji for participant in participants}

        available_emojis = [
            emoji for emoji in self._emoji_pool if emoji not in used_emojis
        ]

        if not available_emojis:
            raise ValueError("No unique emojis remain for this session.")

        emoji = secrets.choice(available_emojis)

        return await self._participants.create(
            session_id=session.sessionid,
            user_id=user_id,
            emoji=emoji,
        )

    async def signoff(
        self,
        *,
        sessionname: str,
        user_id: int,
    ) -> None:
        """Remove a user from an open session."""
        session = await self.get_session(
            sessionname,
            for_update=True,
        )

        if session.status != "new":
            raise ValueError("You cannot leave a session that has started.")

        if (
            await self._participants.get_by_user(
                session.sessionid,
                user_id,
            )
            is None
        ):
            raise ValueError("You are not signed up.")

        await self._participants.delete(
            session_id=session.sessionid,
            user_id=user_id,
        )

    async def get_status(
        self,
        sessionname: str,
    ) -> SessionStatus:
        """Return session details and participant/assignment IDs."""
        session = await self.get_session(sessionname)

        participants = await self._participants.get_by_session(session.sessionid)
        assignments = await self._assignments.get_by_session(session.sessionid)

        return {
            "session": session,
            "participants": [
                participant.participant_id for participant in participants
            ],
            "assignments": [assignment.assignment_id for assignment in assignments],
        }

    async def start_session(
        self,
        sessionname: str,
    ) -> Sessions:
        """Generate and persist assignments, then start the session."""
        session = await self.get_session(
            sessionname,
            for_update=True,
        )

        if session.status != "new":
            raise ValueError("Only new sessions can be started.")

        participants = await self._participants.get_by_session(session.sessionid)

        matching = self._matching_generator.generate(participants)

        for giver, receiver in matching:
            await self._assignments.create(
                session_id=session.sessionid,
                giver_participant_id=giver.participant_id,
                recipient_participant_id=receiver.participant_id,
            )

        updated_session = await self._sessions.update(
            session.sessionid,
            status="started",
            started_at=datetime.now(timezone.utc),
        )

        return updated_session

    async def end_session(
        self,
        sessionname: str,
    ) -> Sessions:
        """Finish the session and reveal the assignments."""
        session = await self.get_session(
            sessionname,
            for_update=True,
        )

        if session.status != "started":
            raise ValueError("Only started sessions can be ended.")

        updated_session = await self._sessions.update(
            session.sessionid,
            status="finished",
            ended_at=datetime.now(timezone.utc),
        )

        return updated_session

    async def list_participants(
        self,
        sessionname: str,
    ) -> list[Participant]:
        session = await self.get_session(sessionname)
        return await self._participants.get_by_session(session.sessionid)

    async def get_participant(
        self,
        *,
        sessionname: str,
        participant_id: int,
    ) -> Participant:
        session = await self.get_session(sessionname)

        participant = await self._participants.get_by_id(
            session.sessionid,
            participant_id,
        )

        if participant is None:
            raise ValueError("Participant does not exist in this session.")

        return participant

    async def list_assignments(
        self,
        sessionname: str,
    ) -> list[GiftAssignment]:
        session = await self.get_session(sessionname)
        return await self._assignments.get_by_session(session.sessionid)

    async def get_assignment(
        self,
        *,
        sessionname: str,
        assignment_id: int,
    ) -> GiftAssignment:
        session = await self.get_session(sessionname)

        assignment = await self._assignments.get_by_id(
            session.sessionid,
            assignment_id,
        )

        if assignment is None:
            raise ValueError("Assignment does not exist in this session.")

        return assignment

    async def get_assignment_giver(
        self,
        *,
        sessionname: str,
        assignment_id: int,
    ) -> dict[str, int | str]:
        session = await self.get_session(sessionname)

        assignment = await self._assignments.get_by_id(
            session.sessionid,
            assignment_id,
        )

        if assignment is None:
            raise ValueError("Assignment does not exist in this session.")

        giver = await self._participants.get_by_id(
            session.sessionid,
            assignment.giver_participant_id,
        )

        if giver is None:
            raise ValueError("Giver participant does not exist.")

        if session.status == "finished":
            user = await self._users.get_by_id(giver.user_id)
            identity = (
                user.username or user.first_name or str(giver.user_id)
                if user is not None
                else str(giver.user_id)
            )
        else:
            identity = giver.emoji

        return {
            "participant_id": giver.participant_id,
            "identity": identity,
        }

    async def get_assignment_receiver(
        self,
        *,
        sessionname: str,
        assignment_id: int,
    ) -> dict[str, int | str]:
        session = await self.get_session(sessionname)

        assignment = await self._assignments.get_by_id(
            session.sessionid,
            assignment_id,
        )

        if assignment is None:
            raise ValueError("Assignment does not exist in this session.")

        receiver = await self._participants.get_by_id(
            session.sessionid,
            assignment.recipient_participant_id,
        )

        if receiver is None:
            raise ValueError("Receiver participant does not exist.")

        user = await self._users.get_by_id(receiver.user_id)
        identity = (
            user.username or user.first_name or str(receiver.user_id)
            if user is not None
            else str(receiver.user_id)
        )

        return {
            "participant_id": receiver.participant_id,
            "identity": identity,
        }
