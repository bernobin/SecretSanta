from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AssignmentResponse")


@_attrs_define
class AssignmentResponse:
    """
    Attributes:
        assignment_id (int):
        giver_session_id (int):
        giver_participant_id (int):
        recipient_participant_id (int):
        recipient_session_id (int):
    """

    assignment_id: int
    giver_session_id: int
    giver_participant_id: int
    recipient_participant_id: int
    recipient_session_id: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assignment_id = self.assignment_id

        giver_session_id = self.giver_session_id

        giver_participant_id = self.giver_participant_id

        recipient_participant_id = self.recipient_participant_id

        recipient_session_id = self.recipient_session_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assignment_id": assignment_id,
                "giver_session_id": giver_session_id,
                "giver_participant_id": giver_participant_id,
                "recipient_participant_id": recipient_participant_id,
                "recipient_session_id": recipient_session_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        assignment_id = d.pop("assignment_id")

        giver_session_id = d.pop("giver_session_id")

        giver_participant_id = d.pop("giver_participant_id")

        recipient_participant_id = d.pop("recipient_participant_id")

        recipient_session_id = d.pop("recipient_session_id")

        assignment_response = cls(
            assignment_id=assignment_id,
            giver_session_id=giver_session_id,
            giver_participant_id=giver_participant_id,
            recipient_participant_id=recipient_participant_id,
            recipient_session_id=recipient_session_id,
        )

        assignment_response.additional_properties = d
        return assignment_response

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
