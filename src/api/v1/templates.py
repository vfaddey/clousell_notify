from fastapi import APIRouter, Depends, HTTPException
from jinja2 import TemplateNotFound
from pydantic import UUID4

from src.api.deps import get_current_admin, get_template_service
from src.exceptions.base import CloudsellNotifyException
from src.schemas.template import TemplateOut, TemplateCreate
from src.services.template_service import TemplateService
from starlette import status

router = APIRouter(prefix='/templates',
                   tags=['Templates'],
                   dependencies=[Depends(get_current_admin)])


@router.post('/', response_model=TemplateOut)
async def create_template(template: TemplateCreate,
                          template_service: TemplateService = Depends(get_template_service)):
    try:
        result = await template_service.create(template)
        return result
    except CloudsellNotifyException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/{template_id}')
async def get_template(template_id: UUID4,
                       template_service: TemplateService = Depends(get_template_service)):
    try:
        result = await template_service.get(template_id)
        return result
    except TemplateNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CloudsellNotifyException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/', response_model=list[TemplateOut])
async def get_templates(template_service: TemplateService = Depends(get_template_service)):
    result = await template_service.get_all()
    return result


@router.delete('/{template_id}')
async def delete_template(template_id: UUID4,
                          template_service: TemplateService = Depends(get_template_service)):
    try:
        result = await template_service.delete(template_id)
        return result
    except TemplateNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CloudsellNotifyException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))