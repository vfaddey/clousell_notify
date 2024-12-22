from uuid import UUID

from src.exceptions.provider import ProviderInsertFailed, ProviderDeleteFailed, ProviderNotFound, ProviderAlreadyExists
from src.models import Provider
from src.repositories.provider_repository import ProviderRepository
from src.schemas.provider import ProviderAdd, ProviderOut


class ProviderService:
    def __init__(self, repository: ProviderRepository):
        self.__repository: ProviderRepository = repository

    async def create(self, provider: ProviderAdd) -> ProviderOut:
        try:
            existing = await self.__repository.get_by_name(provider.name)
            if existing:
                raise ProviderAlreadyExists(f'Provider with name {provider.name} already exists')
            to_insert = Provider(**provider.model_dump())
            inserted = await self.__repository.create(to_insert)
            return ProviderOut.from_orm(inserted)
        except ProviderInsertFailed as e:
            raise ProviderInsertFailed(str(e))

    async def get(self, provider_id: UUID):
        provider = await self.__repository.get(provider_id)
        if not provider:
            raise ProviderNotFound(f'No provider found with provided ID {provider_id}')
        return ProviderOut.from_orm(provider)

    async def get_all(self):
        providers = await self.__repository.get_all()
        return [ProviderOut.from_orm(p) for p in providers]

    async def update(self, provider):
        ...

    async def delete(self, provider_id: UUID):
        try:
            deleted = await self.__repository.delete(provider_id)
            if not deleted:
                raise ProviderNotFound(f'No provider found with provided ID {provider_id}')
            return ProviderOut.from_orm(deleted)
        except ProviderDeleteFailed as e:
            raise ProviderDeleteFailed(str(e))