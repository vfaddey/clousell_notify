from uuid import UUID

from src.core.exceptions import InvalidToken
from src.core.jwt_decoder import JWTDecoder
from src.exceptions.admin import AdminNotFound
from src.exceptions.base import CloudsellNotifyException
from src.repositories.admin_repository import AdminRepository
from src.schemas.admin import AdminSchema


class AdminService:
    def __init__(self, repository: AdminRepository):
        self.__repository = repository

    async def get_by_user_id(self, user_id: UUID) -> AdminSchema:
        try:
            admin = await self.__repository.get(user_id)
            if not admin:
                raise AdminNotFound('No admin with such user id')
            return AdminSchema.from_orm(admin)
        except:
            raise CloudsellNotifyException('Something went wrong')

    async def verify_admin(self, token: str):
        try:
            payload = JWTDecoder.decode(token)
            if not payload.get('sub'):
                raise CloudsellNotifyException('Invalid token')
            admin = await self.__repository.get(payload['sub'])
            if not admin:
                raise AdminNotFound('No admin with such user id')
            return AdminSchema.from_orm(admin)
        except InvalidToken as e:
            raise CloudsellNotifyException(e)