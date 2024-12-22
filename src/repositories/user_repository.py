from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User


class UserRepository(ABC):
    @abstractmethod
    def create(self, user):
        raise NotImplementedError

    @abstractmethod
    def get(self, user_id: int | UUID):
        raise NotImplementedError

    @abstractmethod
    def update(self, user_id: int | UUID, user):
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: int | UUID):
        raise NotImplementedError


class SqlaUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: User) -> User:
        try:
            self._session.add(user)
            await self._session.commit()
            await self._session.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise e

    async def get(self, user_id: int | UUID) -> User:
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar()

    async def update(self, user_id: int | UUID, user: User) -> User:
        try:
            self._session.add(user)
            await self._session.commit()
            await self._session.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise e

    async def delete(self, user_id: int | UUID) -> User:
        try:
            stmt = delete(User).where(User.id == user_id).returning(User)
            result = await self._session.execute(stmt)
            await self._session.commit()
            return result.scalar()
        except SQLAlchemyError as e:
            await self._session.rollback()
