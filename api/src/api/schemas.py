from datetime import datetime

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# USERS


class UserResponse(APIModel):
    userid: int
    chatid: int
    username: str | None
    first_name: str | None
    last_name: str | None


# SESSIONS


class SessionResponse(APIModel):
    sessionid: int
    sessionname: str
    admin_userid: int
    status: str
    seed: str | None
    started_at: datetime | None
    ended_at: datetime | None


class SessionDetailResponse(SessionResponse):
    admin: UserResponse


class SessionStatusResponse(BaseModel):
    session: SessionResponse
    participants: list[int]
    assignments: list[int]


# PARTICIPANTS


class ParticipantResponse(APIModel):
    participant_id: int
    user_id: int
    session_id: int
    signed_up_at: datetime
    emoji: str


# GIFT ASSIGNMENTS


class AssignmentResponse(APIModel):
    assignment_id: int
    giver_session_id: int
    giver_participant_id: int
    recipient_participant_id: int
    recipient_session_id: int


class AssignmentParticipantResponse(BaseModel):
    participant_id: int
    identity: str


# REQUESTS


class CreateUserRequest(BaseModel):
    chatid: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class CreateSessionRequest(BaseModel):
    sessionname: str
    admin_userid: int
    seed: str | None = None


# ERROR


class APIErrorResponse(BaseModel):
    error: str
    message: str


# SIGNUP


class SignupResponse(ParticipantResponse):
    pass
