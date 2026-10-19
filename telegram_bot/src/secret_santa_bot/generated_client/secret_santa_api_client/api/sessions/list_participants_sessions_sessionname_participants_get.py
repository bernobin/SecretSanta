from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.participant_response import ParticipantResponse
from ...types import Response


def _get_kwargs(
    sessionname: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/sessions/{sessionname}/participants".format(
            sessionname=quote(str(sessionname), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[ParticipantResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ParticipantResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | list[ParticipantResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    sessionname: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | list[ParticipantResponse]]:
    """List Participants

    Args:
        sessionname (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[ParticipantResponse]]
    """

    kwargs = _get_kwargs(
        sessionname=sessionname,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    sessionname: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | list[ParticipantResponse] | None:
    """List Participants

    Args:
        sessionname (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[ParticipantResponse]
    """

    return sync_detailed(
        sessionname=sessionname,
        client=client,
    ).parsed


async def asyncio_detailed(
    sessionname: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | list[ParticipantResponse]]:
    """List Participants

    Args:
        sessionname (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[ParticipantResponse]]
    """

    kwargs = _get_kwargs(
        sessionname=sessionname,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    sessionname: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | list[ParticipantResponse] | None:
    """List Participants

    Args:
        sessionname (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[ParticipantResponse]
    """

    return (
        await asyncio_detailed(
            sessionname=sessionname,
            client=client,
        )
    ).parsed
