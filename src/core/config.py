import asyncio
import ssl
from datetime import datetime, timedelta
from os import pread

import certifi
from typing import Optional
import aiohttp

from pathlib import Path
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    APP_NAME: Optional[str] = "CloudSell.Notify Service"

    # db
    DB_TYPE: str = "postgresql"
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_DRIVER: str = 'asyncpg'

    #jwt
    JWT_ALGORITHM: str = "RS256"
    AUTH_SERVER_URL: str
    JWKS_URI: str

    # smtp
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    # rabbitmq
    RABBITMQ_URL: str
    RABBITMQ_QUEUE: str

    __public_key = None
    __public_key_last_update = None

    class Config:
        env_file = ".env"
        extra = 'ignore'

    @property
    def DB_URL(self):
        return f'{self.DB_TYPE}+{self.DB_DRIVER}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}'

    @property
    def JWT_PUBLIC_KEY(self):
        if not self.__public_key_last_update:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.update_public_key())
            else:
                loop.run_until_complete(self.update_public_key())
            self.__public_key_last_update = datetime.utcnow()
        if datetime.utcnow() - self.__public_key_last_update < timedelta(hours=1):
            return self.__public_key
        return self.__public_key

    async def update_public_key(self):
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(self.AUTH_SERVER_URL + self.JWKS_URI) as response:
                    res = await response.json()
                    self.__public_key = res.get('keys', [])[0].get('n', '')
        except:
            raise Exception('Something went wrong, while updating public key')


settings = Settings()
