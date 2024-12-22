from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from starlette import status

from src.api.deps import get_pricing_plan_filter, get_pricing_plan_service, get_current_user, get_current_admin
from src.exceptions.base import CloudSellAPIException
from src.exceptions.pricing_plan import FailedToCreatePlan, PricingPlanNotFound
from src.exceptions.provider import ProviderNotFound
from src.schemas.pricing_plan import PricingPlanFilter, PricingPlanAdd, PricingPlanOut
from src.schemas.user import UserOut
from src.services.pricing_plan_service import PricingPlanService

router = APIRouter(prefix='/servers', tags=['Servers'])



@router.post('/',
             response_model=PricingPlanOut,
             status_code=status.HTTP_201_CREATED,
             description='Создать карточку сервера (pricing plan)',
             dependencies=[Depends(get_current_admin)])
async def create_pricing_plan(pricing_plan: PricingPlanAdd,
                              pricing_plan_service: PricingPlanService = Depends(get_pricing_plan_service)):
    try:
        result = await pricing_plan_service.add(pricing_plan)
        return result
    except ProviderNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FailedToCreatePlan as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/list',
            response_model=list[PricingPlanOut],
            description='Получить список провайдеров. Можно использовать фильтры, иначе выведется список всех.')
async def get_server_list(filters: PricingPlanFilter = Depends(get_pricing_plan_filter),
                          pricing_plan_service: PricingPlanService = Depends(get_pricing_plan_service)):
    try:
        result = await pricing_plan_service.get_by_filter(filters)
        return result
    except ProviderNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get('/{plan_id}',
            response_model=PricingPlanOut,
            description='Получить конфигурацию по ID')
async def get_by_id(plan_id: UUID4,
                    pricing_plan_service: PricingPlanService = Depends(get_pricing_plan_service)):
    try:
        result = await pricing_plan_service.get(plan_id)
        return result
    except PricingPlanNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CloudSellAPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))