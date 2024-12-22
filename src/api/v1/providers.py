from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import UUID4
from starlette import status

from src.api.deps import get_provider_service
from src.exceptions.base import CloudSellAPIException
from src.exceptions.provider import ProviderInsertFailed, ProviderNotFound, ProviderDeleteFailed, ProviderAlreadyExists
from src.schemas.provider import ProviderOut, ProviderAdd
from src.services.provider_service import ProviderService

router = APIRouter(prefix='/providers', tags=['Providers'])


@router.post('',
             response_model=ProviderOut,
             status_code=status.HTTP_201_CREATED,
             description='Создать нового провайдера')
async def create_provider(provider: ProviderAdd,
                          provider_service: ProviderService = Depends(get_provider_service)):
    try:
        result = await provider_service.create(provider)
        return result
    except ProviderAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ProviderInsertFailed as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('',
            response_model=list[ProviderOut],
            description='Получить список провайдеров')
async def get_providers(provider_service: ProviderService = Depends(get_provider_service)):
    providers = await provider_service.get_all()
    return providers


@router.get('/{provider_id}',
            response_model=ProviderOut,
            description='Получить провайдера по ID (UUID)')
async def get_provider_by_id(provider_id: UUID4,
                             provider_service: ProviderService = Depends(get_provider_service)):
    try:
        result = await provider_service.get(provider_id)
        return result
    except ProviderNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CloudSellAPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/{provider_id}',
               response_model=ProviderOut,
               description='Удалить провайдера')
async def delete_provider(provider_id: UUID4,
                          provider_service: ProviderService = Depends(get_provider_service)):
    try:
        result = await provider_service.delete(provider_id)
        return result
    except ProviderNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProviderDeleteFailed as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
