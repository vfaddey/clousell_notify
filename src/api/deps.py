from typing import Optional

from fastapi import Query, HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.adapters.auth.auth_adapter import CloudsellAuthAdapter
from src.core.config import settings
from src.db.database import AsyncSessionFactory
from src.exceptions.base import CloudSellAPIException
from src.exceptions.user import UserNotFound
from src.models import RAMType, DiskType, ServerType, BillingCycle
from src.repositories.pricing_plan_repository import SqlaPricingPlanRepository
from src.repositories.provider_repository import SqlaProviderRepository
from src.repositories.user_repository import SqlaUserRepository
from src.schemas.pricing_plan import PricingPlanFilter
from src.schemas.user import UserOut
from src.services.pricing_plan_service import PricingPlanService
from src.services.provider_service import ProviderService
from src.services.user_service import UserService

http_bearer = HTTPBearer()


async def get_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_provider_service(session: AsyncSession = Depends(get_session)) -> ProviderService:
    repository = SqlaProviderRepository(session)
    return ProviderService(repository)


async def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    repository = SqlaUserRepository(session)
    return UserService(repository)


async def get_pricing_plan_service(session: AsyncSession = Depends(get_session)) -> PricingPlanService:
    pricing_plan_repository = SqlaPricingPlanRepository(session)
    provider_repository = SqlaProviderRepository(session)
    return PricingPlanService(pricing_plan_repository,
                              provider_repository)


async def get_auth_adapter():
    return CloudsellAuthAdapter(settings.AUTH_SERVER_URL,
                                settings.USERINFO_URI)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
                           user_service: UserService = Depends(get_user_service)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        user = await user_service.authorize_user(token)
        return user
    except UserNotFound as e:
        try:
            auth_adapter = await get_auth_adapter()
            user_to_add = await auth_adapter.get_userinfo(token)
            user = await user_service.add(user_to_add)
            return user
        except:
            raise credentials_exception
    except CloudSellAPIException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


async def get_current_admin(user: UserOut = Depends(get_current_user)):
    if user.is_admin:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin")


def get_pricing_plan_filter(
        cores_min: Optional[int] = Query(None, ge=1, description="Минимальное количество ядер"),
        cores_max: Optional[int] = Query(None, ge=1, description="Максимальное количество ядер"),
        core_frequency_min: Optional[float] = Query(None, ge=0, description="Минимальная частота ядра (ГГц)"),
        core_frequency_max: Optional[float] = Query(None, ge=0, description="Максимальная частота ядра (ГГц)"),
        ram_min: Optional[float] = Query(None, ge=0, description="Минимальный объем оперативной памяти (GB)"),
        ram_max: Optional[float] = Query(None, ge=0, description="Максимальный объем оперативной памяти (GB)"),
        ram_type: Optional[RAMType] = Query(None, description="Тип оперативной памяти"),
        disk_min: Optional[float] = Query(None, ge=0, description="Минимальный объем диска (GB)"),
        disk_max: Optional[float] = Query(None, ge=0, description="Максимальный объем диска (GB)"),
        disk_type: Optional[DiskType] = Query(None, description="Тип диска"),
        network_speed_min: Optional[float] = Query(None, ge=0, description="Минимальная скорость сети (Mbps)"),
        network_limit_min: Optional[float] = Query(None, ge=0, description="Минимальный лимит сети (GB)"),
        location: Optional[list[str]] = Query(None, description="Местоположения (можно несколько)"),
        price_min: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
        price_max: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
        server_type: Optional[ServerType] = Query(None, description="Тип сервера (virtual или dedicated)"),
        billing_cycle: Optional[BillingCycle] = Query(None, description="Цикл биллинга (monthly или annually)"),
        min_rating: Optional[float] = Query(None, ge=0, le=5, description="Минимальный рейтинг провайдера"),
        provider_id: Optional[UUID4] = Query(None, description='ID провайдера'),
        sort_by: Optional[str] = Query(None, description="Поле для сортировки (price, rating)"),
        sort_order: Optional[str] = Query('asc', description="Порядок сортировки (asc или desc)"),
        skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
        limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей")
) -> PricingPlanFilter:

    valid_ram_types = {ram.value for ram in RAMType}
    if ram_type and ram_type not in valid_ram_types:
        raise HTTPException(status_code=400, detail=f"Invalid ram_type. Must be one of {valid_ram_types}")

    valid_disk_types = {disk.value for disk in DiskType}
    if disk_type and disk_type not in valid_disk_types:
        raise HTTPException(status_code=400, detail=f"Invalid disk_type. Must be one of {valid_disk_types}")

    valid_server_types = {server.value for server in ServerType}
    if server_type and server_type not in valid_server_types:
        raise HTTPException(status_code=400, detail=f"Invalid server_type. Must be one of {valid_server_types}")

    valid_billing_cycles = {cycle.value for cycle in BillingCycle}
    if billing_cycle and billing_cycle not in valid_billing_cycles:
        raise HTTPException(status_code=400, detail=f"Invalid billing_cycle. Must be one of {valid_billing_cycles}")

    valid_sort_fields = {'price', 'rating'}
    if sort_by and sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by. Must be one of {valid_sort_fields}")

    if sort_order not in {'asc', 'desc'}:
        raise HTTPException(status_code=400, detail="Invalid sort_order. Must be 'asc' or 'desc'")

    return PricingPlanFilter(
        cores_min=cores_min,
        cores_max=cores_max,
        core_frequency_min=core_frequency_min,
        core_frequency_max=core_frequency_max,
        ram_min=ram_min,
        ram_max=ram_max,
        ram_type=ram_type,
        disk_min=disk_min,
        disk_max=disk_max,
        disk_type=disk_type,
        network_speed_min=network_speed_min,
        network_limit_min=network_limit_min,
        location=location,
        price_min=price_min,
        price_max=price_max,
        server_type=server_type,
        billing_cycle=billing_cycle,
        min_rating=min_rating,
        provider_id=provider_id,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )