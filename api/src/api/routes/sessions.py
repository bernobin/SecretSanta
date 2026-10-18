from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.api.dependencies import ApplicationServices, get_services
from src.api.schemas import (
    AssignmentParticipantResponse,
    AssignmentResponse,
    CreateSessionRequest,
    ParticipantResponse,
    SessionResponse,
    SessionStatusResponse,
    SignupResponse,
)

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    request: CreateSessionRequest,
    services: ApplicationServices = Depends(get_services),
) -> SessionResponse:
    try:
        session = await services.sessions.create_session(
            sessionname=request.sessionname,
            admin_userid=request.admin_userid,
            seed=request.seed,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return SessionResponse.model_validate(session)


@router.get(
    "/{sessionname}",
    response_model=SessionStatusResponse,
)
async def get_status(
    sessionname: str,
    services: ApplicationServices = Depends(get_services),
) -> SessionStatusResponse:
    try:
        result = await services.sessions.get_status(sessionname)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return SessionStatusResponse.model_validate(result)


@router.post(
    "/{sessionname}/participants/{user_id}",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    sessionname: str,
    user_id: int,
    services: ApplicationServices = Depends(get_services),
) -> SignupResponse:
    try:
        participant = await services.sessions.signup(
            sessionname=sessionname,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return SignupResponse.model_validate(participant)


@router.delete(
    "/{sessionname}/participants/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def signoff(
    sessionname: str,
    user_id: int,
    services: ApplicationServices = Depends(get_services),
) -> Response:
    try:
        await services.sessions.signoff(
            sessionname=sessionname,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{sessionname}/participants",
    response_model=list[ParticipantResponse],
)
async def list_participants(
    sessionname: str,
    services: ApplicationServices = Depends(get_services),
) -> list[ParticipantResponse]:
    try:
        participants = await services.sessions.list_participants(sessionname)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return [
        ParticipantResponse.model_validate(participant) for participant in participants
    ]


@router.get(
    "/{sessionname}/participants/{participant_id}",
    response_model=ParticipantResponse,
)
async def get_participant(
    sessionname: str,
    participant_id: int,
    services: ApplicationServices = Depends(get_services),
) -> ParticipantResponse:
    try:
        participant = await services.sessions.get_participant(
            sessionname=sessionname,
            participant_id=participant_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ParticipantResponse.model_validate(participant)


@router.get(
    "/{sessionname}/assignments",
    response_model=list[AssignmentResponse],
)
async def list_assignments(
    sessionname: str,
    services: ApplicationServices = Depends(get_services),
) -> list[AssignmentResponse]:
    try:
        assignments = await services.sessions.list_assignments(sessionname)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return [AssignmentResponse.model_validate(assignment) for assignment in assignments]


@router.get(
    "/{sessionname}/assignments/{assignment_id}",
    response_model=AssignmentResponse,
)
async def get_assignment(
    sessionname: str,
    assignment_id: int,
    services: ApplicationServices = Depends(get_services),
) -> AssignmentResponse:
    try:
        assignment = await services.sessions.get_assignment(
            sessionname=sessionname,
            assignment_id=assignment_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return AssignmentResponse.model_validate(assignment)


@router.get(
    "/{sessionname}/assignments/{assignment_id}/giver",
    response_model=AssignmentParticipantResponse,
)
async def get_assignment_giver(
    sessionname: str,
    assignment_id: int,
    services: ApplicationServices = Depends(get_services),
) -> AssignmentParticipantResponse:
    try:
        result = await services.sessions.get_assignment_giver(
            sessionname=sessionname,
            assignment_id=assignment_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return AssignmentParticipantResponse.model_validate(result)


@router.get(
    "/{sessionname}/assignments/{assignment_id}/receiver",
    response_model=AssignmentParticipantResponse,
)
async def get_assignment_receiver(
    sessionname: str,
    assignment_id: int,
    services: ApplicationServices = Depends(get_services),
) -> AssignmentParticipantResponse:
    try:
        result = await services.sessions.get_assignment_receiver(
            sessionname=sessionname,
            assignment_id=assignment_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return AssignmentParticipantResponse.model_validate(result)


@router.post(
    "/{sessionname}/start",
    response_model=SessionResponse,
)
async def start_session(
    sessionname: str,
    services: ApplicationServices = Depends(get_services),
) -> SessionResponse:
    try:
        session = await services.sessions.start_session(sessionname)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return SessionResponse.model_validate(session)


@router.post(
    "/{sessionname}/end",
    response_model=SessionResponse,
)
async def end_session(
    sessionname: str,
    services: ApplicationServices = Depends(get_services),
) -> SessionResponse:
    try:
        session = await services.sessions.end_session(sessionname)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return SessionResponse.model_validate(session)
