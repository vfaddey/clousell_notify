from abc import ABC, abstractmethod
import aiohttp

from src.exceptions.base import CloudSellAPIException
from src.schemas.user import UserAdd


class AuthAdapter(ABC):
    def __init__(self,
                 auth_server_url,
                 userinfo_uri):
        self._auth_server_url = auth_server_url
        self._userinfo_uri = userinfo_uri

    @abstractmethod
    def get_userinfo(self, token):
        raise NotImplementedError


class CloudsellAuthAdapter(AuthAdapter):
    async def get_userinfo(self, token):
        try:
            async with aiohttp.ClientSession() as session:
                data = await self.__fetch_user(session, token)
                return UserAdd(**data)
        except:
            raise CloudSellAPIException('Something went wrong, while getting user data')


    async def __fetch_user(self, session, token: str = None):
        if token:
            headers = {'Authorization': f'Bearer {token}'}
            async with session.get(self._auth_server_url + self._userinfo_uri, headers=headers) as response:
                return await response.json()
        async with session.get(self._auth_server_url + self._userinfo_uri) as response:
            return await response.json()