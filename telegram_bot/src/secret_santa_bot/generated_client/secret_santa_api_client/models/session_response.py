from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SessionResponse")


@_attrs_define
class SessionResponse:
    """
    Attributes:
        sessionid (int):
        sessionname (str):
        admin_userid (int):
        status (str):
        seed (None | str):
        started_at (datetime.datetime | None):
        ended_at (datetime.datetime | None):
    """

    sessionid: int
    sessionname: str
    admin_userid: int
    status: str
    seed: None | str
    started_at: datetime.datetime | None
    ended_at: datetime.datetime | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sessionid = self.sessionid

        sessionname = self.sessionname

        admin_userid = self.admin_userid

        status = self.status

        seed: None | str
        seed = self.seed

        started_at: None | str
        if isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        ended_at: None | str
        if isinstance(self.ended_at, datetime.datetime):
            ended_at = self.ended_at.isoformat()
        else:
            ended_at = self.ended_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sessionid": sessionid,
                "sessionname": sessionname,
                "admin_userid": admin_userid,
                "status": status,
                "seed": seed,
                "started_at": started_at,
                "ended_at": ended_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sessionid = d.pop("sessionid")

        sessionname = d.pop("sessionname")

        admin_userid = d.pop("admin_userid")

        status = d.pop("status")

        def _parse_seed(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        seed = _parse_seed(d.pop("seed"))

        def _parse_started_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = datetime.datetime.fromisoformat(data)

                return started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        started_at = _parse_started_at(d.pop("started_at"))

        def _parse_ended_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                ended_at_type_0 = datetime.datetime.fromisoformat(data)

                return ended_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        ended_at = _parse_ended_at(d.pop("ended_at"))

        session_response = cls(
            sessionid=sessionid,
            sessionname=sessionname,
            admin_userid=admin_userid,
            status=status,
            seed=seed,
            started_at=started_at,
            ended_at=ended_at,
        )

        session_response.additional_properties = d
        return session_response

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
