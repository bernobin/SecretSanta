from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.signup_response import SignupResponse
from ...types import Response


def _get_kwargs(
    sessionname: str,
    user_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/sessions/{sessionname}/participants/{user_id}".format(
            sessionname=quote(str(sessionname), safe=""),
            user_id=quote(str(user_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SignupResponse | None:
    if response.status_code == 201:
        response_201 = SignupResponse.from_dict(response.json())

        return response_201

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | SignupResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    sessionname: str,
    user_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | SignupResponse]:
    """Signup

    Args:
        sessionname (str):
        user_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SignupResponse]
    """

    kwargs = _get_kwargs(
        sessionname=sessionname,
        user_id=user_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    sessionname: str,
    user_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | SignupResponse | None:
    """Signup

    Args:
        sessionname (str):
        user_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SignupResponse
    """

    return sync_detailed(
        sessionname=sessionname,
        user_id=user_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    sessionname: str,
    user_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | SignupResponse]:
    """Signup

    Args:
        sessionname (str):
        user_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SignupResponse]
    """

    kwargs = _get_kwargs(
        sessionname=sessionname,
        user_id=user_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    sessionname: str,
    user_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | SignupResponse | None:
    """Signup

    Args:
        sessionname (str):
        user_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SignupResponse
    """

    return (
        await asyncio_detailed(
            sessionname=sessionname,
            user_id=user_id,
            client=client,
        )
    ).parsed
