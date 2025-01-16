from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.admin import Admin


class AdminRepository(ABC):
    @abstractmethod
    async def get(self, user_id: int | UUID):
        raise NotImplementedError


class SqlaAdminRepository(AdminRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, user_id: int | UUID) -> Admin:
        stmt = select(Admin).where(Admin.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.unique().scalars().first()
