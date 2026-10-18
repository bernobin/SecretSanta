
import logging
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class SecretSantaAPI:
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(10.0, connect=5.0),
        )

    async def close(self):
        await self.client.aclose()

    async def request(self, method: str, path: str, **kwargs):
        try:
            response = await self.client.request(
                method, path, **kwargs
            )
        except httpx.HTTPError as exc:
            logger.warning("API connection error: %s", exc)
            raise APIError(0, "The API is unavailable.") from exc


        if not response.is_success:
            logger.warning(
                "%s %s returned HTTP %s: %s",
                method, path, response.status_code, response.text[:500],
            )

            try:
                data = response.json()
                message = data.get("detail", "The request failed. Please try again.")
                if not isinstance(message, str):
                    message = "The request failed. Please try again."
            except ValueError:
                message = "The request failed. Please try again."

            raise APIError(response.status_code, message)

        if response.status_code == 204 or not response.content:
            return None

        try:
            return response.json()
        except ValueError as exc:
            raise APIError(
                response.status_code, "Invalid API response."
            ) from exc

    async def create_user(self, telegram_user):
        return await self.request(
            "POST",
            "/users",
            json={
                "chatid": telegram_user.id,
                "username": telegram_user.username,
                "first_name": telegram_user.first_name,
                "last_name": telegram_user.last_name,
            },
        )

    async def get_user_by_chat_id(self, chat_id: int):
        # This matches the filter syntax supported by your API.
        users = await self.request(
            "GET",
            "/users",
            params={"$filter": f"chatid eq {chat_id}"},
        )

        if not isinstance(users, list):
            raise APIError(200, "Unexpected user list response.")

        matches = [
            user for user in users
            if user.get("chatid") == chat_id
        ]

        if len(matches) > 1:
            raise APIError(200, "Duplicate Telegram user records.")

        return matches[0] if matches else None

    async def get_user(self, user_id: int):
        return await self.request("GET", f"/users/{user_id}")

    async def create_session(self, name: str, admin_userid: int):
        return await self.request(
            "POST",
            "/sessions",
            json={
                "sessionname": name,
                "admin_userid": admin_userid,
            },
        )

    async def get_session_status(self, name: str):
        return await self.request(
            "GET", f"/sessions/{quote(name, safe='')}"
        )

    async def get_participants(self, name: str):
        return await self.request(
            "GET", f"/sessions/{quote(name, safe='')}/participants"
        )

    async def join(self, name: str, user_id: int):
        return await self.request(
            "POST",
            f"/sessions/{quote(name, safe='')}/participants/{user_id}",
        )

    async def leave(self, name: str, user_id: int):
        return await self.request(
            "DELETE",
            f"/sessions/{quote(name, safe='')}/participants/{user_id}",
        )

    async def get_assignments(self, name: str):
        return await self.request(
            "GET", f"/sessions/{quote(name, safe='')}/assignments"
        )

    async def get_giver(self, name: str, assignment_id: int):
        return await self.request(
            "GET",
            f"/sessions/{quote(name, safe='')}/assignments/"
            f"{assignment_id}/giver",
        )

    async def get_receiver(self, name: str, assignment_id: int):
        return await self.request(
            "GET",
            f"/sessions/{quote(name, safe='')}/assignments/"
            f"{assignment_id}/receiver",
        )

    async def start_session(self, name: str):
        return await self.request(
            "POST", f"/sessions/{quote(name, safe='')}/start"
        )

    async def end_session(self, name: str):
        return await self.request(
            "POST", f"/sessions/{quote(name, safe='')}/end"
        )
