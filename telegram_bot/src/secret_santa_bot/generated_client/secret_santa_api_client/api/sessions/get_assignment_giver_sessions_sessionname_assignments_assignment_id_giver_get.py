from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assignment_participant_response import AssignmentParticipantResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    sessionname: str,
    assignment_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/sessions/{sessionname}/assignments/{assignment_id}/giver".format(
            sessionname=quote(str(sessionname), safe=""),
            assignment_id=quote(str(assignment_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AssignmentParticipantResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AssignmentParticipantResponse.from_dict(response.json())

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
) -> Response[AssignmentParticipantResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    sessionname: str,
    assignment_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[AssignmentParticipantResponse | HTTPValidationError]:
    """Get Assignment Giver

    Args:
        sessionname (str):
        assignment_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AssignmentParticipantResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        sessionname=sessionname,
        assignment_id=assignment_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    sessionname: str,
    assignment_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> AssignmentParticipantResponse | HTTPValidationError | None:
    """Get Assignment Giver

    Args:
        sessionname (str):
        assignment_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AssignmentParticipantResponse | HTTPValidationError
    """

    return sync_detailed(
        sessionname=sessionname,
        assignment_id=assignment_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    sessionname: str,
    assignment_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[AssignmentParticipantResponse | HTTPValidationError]:
    """Get Assignment Giver

    Args:
        sessionname (str):
        assignment_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AssignmentParticipantResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        sessionname=sessionname,
        assignment_id=assignment_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    sessionname: str,
    assignment_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> AssignmentParticipantResponse | HTTPValidationError | None:
    """Get Assignment Giver

    Args:
        sessionname (str):
        assignment_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AssignmentParticipantResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            sessionname=sessionname,
            assignment_id=assignment_id,
            client=client,
        )
    ).parsed
