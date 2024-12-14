from typing import Optional

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
    JWT_PUBLIC_KEY_PATH: Path
    JWT_ALGORITHM: str = "RS256"

    # smtp
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    # rabbitmq
    RABBITMQ_URL: str
    RABBITMQ_QUEUE: str

    __public_key = None

    class Config:
        env_file = ".env"
        extra = 'ignore'

    @property
    def DB_URL(self):
        return f'{self.DB_TYPE}+{self.DB_DRIVER}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}'

    @property
    def JWT_PUBLIC_KEY(self):
        if not self.__public_key:
            with open(self.JWT_PUBLIC_KEY_PATH) as f:
                self.__public_key = f.read()
                return self.__public_key
        return self.__public_key


settings = Settings()
