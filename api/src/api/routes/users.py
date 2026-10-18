import re
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies import ApplicationServices, get_services
from src.api.schemas import CreateUserRequest, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: CreateUserRequest,
    services: ApplicationServices = Depends(get_services),
) -> UserResponse:
    user = await services.users.create_user(
        username=request.username or "",
        first_name=request.first_name or "",
        last_name=request.last_name or "",
        chatid=request.chatid,
    )

    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=list[UserResponse],
)
async def list_users(
    filter_expression: Annotated[
        str,
        Query(alias="$filter"),
    ],
    services: ApplicationServices = Depends(get_services),
) -> list[UserResponse]:
    match = re.fullmatch(
        r"\s*chatid\s+eq\s+(\d+)\s*",
        filter_expression,
        flags=re.IGNORECASE,
    )

    if not match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported filter: chatid eq <integer>",
        )

    chatid = int(match.group(1))
    user = await services.users.get_by_chatid(chatid)

    if user is None:
        return []

    return [UserResponse.model_validate(user)]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int,
    services: ApplicationServices = Depends(get_services),
) -> UserResponse:
    try:
        user = await services.users.get_user(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return UserResponse.model_validate(user)
