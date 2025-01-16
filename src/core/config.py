import asyncio
import ssl
from datetime import datetime, timedelta

import certifi
from typing import Optional
import aiohttp
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

    __public_key: Optional[str] = None
    __public_key_last_update: Optional[datetime] = None
    __lock = asyncio.Lock()

    class Config:
        env_file = ".env"
        extra = 'ignore'

    @property
    def DB_URL(self):
        return f'{self.DB_TYPE}+{self.DB_DRIVER}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}'

    @property
    def JWT_PUBLIC_KEY(self):
        if not self.__public_key or datetime.utcnow() - self.__public_key_last_update >= timedelta(hours=1):
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._update_public_key())
            else:
                loop.run_until_complete(self._update_public_key())
        return self.__public_key

    async def _update_public_key(self):
        async with self.__lock:
            if not self.__public_key or datetime.utcnow() - self.__public_key_last_update >= timedelta(hours=1):
                try:
                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                    connector = aiohttp.TCPConnector(ssl=ssl_context)
                    async with aiohttp.ClientSession(connector=connector) as session:
                        async with session.get(self.AUTH_SERVER_URL + self.JWKS_URI) as response:
                            if response.status == 200:
                                res = await response.json()
                                self.__public_key = res.get('keys', [])[0].get('n', '')
                                self.__public_key_last_update = datetime.utcnow()
                            else:
                                raise Exception(f"Failed to fetch JWKS: {response.status} {response.reason}")
                except Exception as e:
                    self.__public_key = None  # Reset key on failure
                    self.__public_key_last_update = None
                    raise Exception(f"Error updating public key: {str(e)}")


settings = Settings()
