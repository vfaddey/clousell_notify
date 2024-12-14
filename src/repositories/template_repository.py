from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.templates import Template


class TemplateRepository(ABC):

    @abstractmethod
    async def create(self, template):
        raise NotImplementedError

    @abstractmethod
    async def update(self, template):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, template_id: int | UUID):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self):
        raise NotImplementedError

    @abstractmethod
    async def get(self, template_id: int | UUID):
        raise NotImplementedError


class SqlaTemplateRepository(TemplateRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, template: Template):
        try:
            self._session.add(template)
            await self._session.commit()
            await self._session.refresh(template)
            return template
        except:
            await self._session.rollback()
            raise

    async def update(self, template):
        try:
            self._session.add(template)
            await self._session.commit()
            await self._session.refresh(template)
            return template
        except:
            await self._session.rollback()
            raise

    async def delete(self, template_id: int | UUID):
        stmt = delete(Template).where(Template.id == template_id).returning(Template)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalars().first()

    async def get_all(self):
        stmt = select(Template)
        result = await self._session.execute(stmt)
        return result.unique().scalars().all()

    async def get(self, template_id: int | UUID):
        stmt = select(Template).where(Template.id == template_id)
        result = await self._session.execute(stmt)
        return result.unique().scalars().first()