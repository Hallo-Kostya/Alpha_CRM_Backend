from uuid import UUID

from aiohttp import ClientSession
from fastapi import Request
from app.sdk.common.http_client import HttpClient
from app.core.config import settings


class VkBotBackendSdk:
    def __init__(self, http_session: ClientSession):
        self._http_client = HttpClient(http_session)
        self._base_url = settings.vk_bot.base_url
        self.__auth_headers: dict = {
            "Authorization": settings.vk_bot.api_key,
        }

    async def post_declined_application(
        self, vk_sender_id: int, project_name: str, team_name: str
    ) -> None:
        url = f"{self._base_url}/{vk_sender_id}/notify_decline/"
        data = {
            "project_name": project_name,
            "team_name": team_name,
        }
        await self._http_client.post(url, json=data, headers=self.__auth_headers)

    async def post_accepted_application(
        self, vk_sender_id: int, project_name: str, team_name: str
    ) -> None:
        url = f"{self._base_url}/{vk_sender_id}/notify_accept/"
        data = {
            "project_name": project_name,
            "team_name": team_name,
        }
        await self._http_client.post(url, json=data, headers=self.__auth_headers)

    async def post_interview_possible_dates(
        self,
        vk_sender_id: int,
        possible_dates: list[str],
        project_name: str,
        team_name: str,
        application_id: UUID,
    ) -> None:
        url = f"{self._base_url}/{vk_sender_id}/notify_interview/choose_date/"
        data = {
            "application_id": str(application_id),
            "possible_dates": possible_dates,
            "project_name": project_name,
            "team_name": team_name,
        }
        await self._http_client.post(url, json=data, headers=self.__auth_headers)

    async def post_interview_update(
        self,
        vk_sender_id: int,
        project_name: str,
        team_name: str,
        url: str | None = None,
        date: str | None = None,
    ) -> None:
        if not (url or date):
            raise ValueError("Passed None url and date, at least one must be not None")
        request_url = f"{self._base_url}/{vk_sender_id}/notify_interview/update/"
        data = {
            "url": url,
            "date": date,
            "project_name": project_name,
            "team_name": team_name,
        }
        await self._http_client.post(
            request_url, json=data, headers=self.__auth_headers
        )


def get_sdk(request: Request) -> VkBotBackendSdk:
    return request.app.state.vk_bot_backend_sdk
