from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ParticipantResponse")


@_attrs_define
class ParticipantResponse:
    """
    Attributes:
        participant_id (int):
        user_id (int):
        session_id (int):
        signed_up_at (datetime.datetime):
        emoji (str):
    """

    participant_id: int
    user_id: int
    session_id: int
    signed_up_at: datetime.datetime
    emoji: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        participant_id = self.participant_id

        user_id = self.user_id

        session_id = self.session_id

        signed_up_at = self.signed_up_at.isoformat()

        emoji = self.emoji

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "participant_id": participant_id,
                "user_id": user_id,
                "session_id": session_id,
                "signed_up_at": signed_up_at,
                "emoji": emoji,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        participant_id = d.pop("participant_id")

        user_id = d.pop("user_id")

        session_id = d.pop("session_id")

        signed_up_at = datetime.datetime.fromisoformat(d.pop("signed_up_at"))

        emoji = d.pop("emoji")

        participant_response = cls(
            participant_id=participant_id,
            user_id=user_id,
            session_id=session_id,
            signed_up_at=signed_up_at,
            emoji=emoji,
        )

        participant_response.additional_properties = d
        return participant_response

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
