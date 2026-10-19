from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UserResponse")


@_attrs_define
class UserResponse:
    """
    Attributes:
        userid (int):
        chatid (int):
        username (None | str):
        first_name (None | str):
        last_name (None | str):
    """

    userid: int
    chatid: int
    username: None | str
    first_name: None | str
    last_name: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        userid = self.userid

        chatid = self.chatid

        username: None | str
        username = self.username

        first_name: None | str
        first_name = self.first_name

        last_name: None | str
        last_name = self.last_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "userid": userid,
                "chatid": chatid,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        userid = d.pop("userid")

        chatid = d.pop("chatid")

        def _parse_username(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        username = _parse_username(d.pop("username"))

        def _parse_first_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        first_name = _parse_first_name(d.pop("first_name"))

        def _parse_last_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_name = _parse_last_name(d.pop("last_name"))

        user_response = cls(
            userid=userid,
            chatid=chatid,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        user_response.additional_properties = d
        return user_response

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
