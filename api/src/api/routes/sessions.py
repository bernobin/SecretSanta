from fastapi import APIRouter, Depends, status

from api.src.api.dependencies import ApplicationServices, get_services
from api.src.api.schemas import (
    CreateSessionRequest,
    SessionResponse,
    SessionStatusResponse,
    SignupResponse,
    StartSessionResponse,
    EndSessionResponse,
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
    session = await services.sessions.create_session(
        sessionname=request.sessionname,
        admin_userid=request.admin_userid,
        seed=request.seed,
    )
    return SessionResponse.model_validate(session)


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
    participant = await services.sessions.signup(
        sessionname=sessionname,
        user_id=user_id,
    )
    return SignupResponse.model_validate(participant)


@router.delete(
    "/{sessionname}/participants/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def signoff(
    sessionname: str,
    user_id: int,
    services: ApplicationServices = Depends(get_services),
) -> None:
    await services.sessions.signoff(
        sessionname=sessionname,
        user_id=user_id,
    )


@router.get(
    "/{sessionname}",
    response_model=SessionStatusResponse,
)
async def get_status(
    sessionname: str,
    services: ApplicationServices = Depends(get_services),
) -> SessionStatusResponse:
    result = await services.sessions.get_status(sessionname)
    return SessionStatusResponse.model_validate(result)


@router.post(
    "/{sessionname}/start",
    response_model=StartSessionResponse,
)
async def start_session(
    sessionname: str,
    services: ApplicationServices = Depends(get_services),
) -> StartSessionResponse:
    result = await services.sessions.start_session(sessionname)
    return StartSessionResponse.model_validate(result)


@router.post(
    "/{sessionname}/end",
    response_model=EndSessionResponse,
)
async def end_session(
    sessionname: str,
    services: ApplicationServices = Depends(get_services),
) -> EndSessionResponse:
    result = await services.sessions.end_session(sessionname)
    return EndSessionResponse.model_validate(result)