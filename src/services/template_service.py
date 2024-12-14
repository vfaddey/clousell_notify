from uuid import UUID

from src.exceptions.base import CloudsellNotifyException
from src.exceptions.template import TemplateInsertFailed, NoSuchTemplate
from src.models import Template
from src.repositories.template_repository import TemplateRepository
from src.schemas.template import TemplateCreate, TemplateOut


class TemplateService:
    def __init__(self, repository: TemplateRepository):
        self.__repository = repository

    async def create(self, template: TemplateCreate) -> TemplateOut:
        try:
            to_insert = Template(**template.model_dump())
            template = await self.__repository.create(to_insert)
            return TemplateOut.from_orm(template)
        except Exception as e:
            print(e)
            raise TemplateInsertFailed('Failed to create template')

    async def get(self, template_id: UUID) -> TemplateOut:
        result = await self.__repository.get(template_id)
        if not result:
            raise NoSuchTemplate(f'Template with id {template_id} not found')
        return TemplateOut.from_orm(result)

    async def get_all(self) -> list[TemplateOut]:
        result = await self.__repository.get_all()
        return [TemplateOut.from_orm(t) for t in result]

    async def delete(self, template_id: UUID):
        try:
            result = await self.__repository.delete(template_id)
            if not result:
                raise NoSuchTemplate(f'Template with id {template_id} not found')
            return result
        except:
            raise CloudsellNotifyException('Failed to delete template')

    async def update(self):
        ...
