from uuid import UUID

from src.core.exceptions import InvalidToken
from src.core.jwt_decoder import JWTDecoder
from src.exceptions.base import CloudSellAPIException
from src.exceptions.user import UserNotFound
from src.models import User
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserAdd, UserOut


class UserService:
    def __init__(self, repository: UserRepository):
        self.__repository = repository

    async def add(self, user: UserAdd) -> UserOut:
        to_insert = User(**user.model_dump())
        inserted = await self.__repository.create(to_insert)
        return UserOut.from_orm(inserted)

    async def get(self, user_id: UUID) -> UserOut:
        user = await self.__repository.get(user_id)
        if not user:
            raise UserNotFound(f'No user with id {user_id}')
        return UserOut.from_orm(user)

    async def authorize_user(self, token: str):
        try:
            payload = JWTDecoder.decode(token)
            if not payload.get('sub'):
                raise CloudSellAPIException('Invalid token')
            admin = await self.__repository.get(payload['sub'])
            if not admin:
                raise UserNotFound(f'No user with such user id {payload.get("sub")}')
            return UserOut.from_orm(admin)
        except InvalidToken as e:
            raise CloudSellAPIException(e)
