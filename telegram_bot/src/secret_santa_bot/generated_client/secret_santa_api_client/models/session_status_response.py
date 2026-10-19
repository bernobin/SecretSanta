from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.session_response import SessionResponse


T = TypeVar("T", bound="SessionStatusResponse")


@_attrs_define
class SessionStatusResponse:
    """
    Attributes:
        session (SessionResponse):
        participants (list[int]):
        assignments (list[int]):
    """

    session: SessionResponse
    participants: list[int]
    assignments: list[int]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        session = self.session.to_dict()

        participants = self.participants

        assignments = self.assignments

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "session": session,
                "participants": participants,
                "assignments": assignments,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.session_response import SessionResponse  # noqa: PLC0415

        d = dict(src_dict)
        session = SessionResponse.from_dict(d.pop("session"))

        participants = cast(list[int], d.pop("participants"))

        assignments = cast(list[int], d.pop("assignments"))

        session_status_response = cls(
            session=session,
            participants=participants,
            assignments=assignments,
        )

        session_status_response.additional_properties = d
        return session_status_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
