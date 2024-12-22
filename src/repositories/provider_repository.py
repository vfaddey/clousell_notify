from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select, delete, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.provider import ProviderDeleteFailed, ProviderInsertFailed
from src.models import Provider


class ProviderRepository(ABC):
    @abstractmethod
    def create(self, provider):
        raise NotImplementedError

    @abstractmethod
    def get(self, provider_id: int | UUID):
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, provider_name: str):
        raise NotImplementedError

    @abstractmethod
    def get_all(self):
        raise NotImplementedError

    @abstractmethod
    def update(self, provider):
        raise NotImplementedError

    @abstractmethod
    def delete(self, provider_id: int | UUID):
        raise NotImplementedError


class SqlaProviderRepository(ProviderRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, provider: Provider) -> Provider:
        try:
            self._session.add(provider)
            await self._session.commit()
            await self._session.refresh(provider)
            return provider
        except SQLAlchemyError as e:
            print(e)
            await self._session.rollback()
            raise ProviderInsertFailed('Failed to create provider')

    async def get(self, provider_id: UUID) -> Provider:
        stmt = select(Provider).where(Provider.id == provider_id)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_by_name(self, provider_name: str) -> Provider:
        stmt = select(Provider).where(Provider.name == provider_name)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> list[Provider]:
        stmt = select(Provider)
        result = await self._session.execute(stmt)
        return list(result.unique().scalars().all())

    async def update(self, provider: Provider) -> Provider:
        try:
            self._session.add(provider)
            await self._session.commit()
            await self._session.refresh(provider)
            return provider
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise e

    async def delete(self, provider_id: UUID) -> Provider:
        try:
            stmt = delete(Provider).where(Provider.id == provider_id).returning(Provider)
            result = await self._session.execute(stmt)
            await self._session.commit()
            return result.scalars().first()
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise ProviderDeleteFailed('Failed to delete provider')
