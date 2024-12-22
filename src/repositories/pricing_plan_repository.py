from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, delete, ColumnElement
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.exceptions.pricing_plan import PlanInsertFailed
from src.models import PricingPlan, Features, Provider
from src.schemas.pricing_plan import PricingPlanFilter


class PricingPlanRepository(ABC):
    @abstractmethod
    def create(self, pricing_plan):
        raise NotImplementedError

    @abstractmethod
    def get(self, plan_id: int | UUID):
        raise NotImplementedError

    @abstractmethod
    def get_all(self):
        raise NotImplementedError

    @abstractmethod
    def get_by_provider(self, provider_id):
        raise NotImplementedError

    @abstractmethod
    def get_by_filter(self, filter):
        raise NotImplementedError

    @abstractmethod
    def update(self, plan_id: int | UUID, pricing_plan):
        raise NotImplementedError

    @abstractmethod
    def delete(self, plan_id: int | UUID):
        raise NotImplementedError


class FilterBuilder:
    def __init__(self):
        self.__conditions = []

    def add_condition(self, condition: Optional[bool | ColumnElement[bool]]):
        if condition is not None:
            self.__conditions.append(condition)

    def build(self):
        return and_(*self.__conditions) if self.__conditions else None


class SqlaPricingPlanRepository(PricingPlanRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, pricing_plan: PricingPlan):
        try:
            self._session.add(pricing_plan)
            await self._session.commit()
            await self._session.refresh(pricing_plan)
            return pricing_plan
        except SQLAlchemyError as e:
            raise PlanInsertFailed('Failed to create pricing plan', e)

    async def get(self, plan_id: int | UUID) -> PricingPlan:
        stmt = select(PricingPlan).where(PricingPlan.id == plan_id)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_all(self):
        stmt = select(PricingPlan)
        result = await self._session.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_provider(self, provider_id):
        stmt = select(PricingPlan).where(PricingPlan.provider_id == provider_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_filter(self, filters: PricingPlanFilter):
        stmt = select(PricingPlan)
        builder = FilterBuilder()

        stmt = stmt.join(PricingPlan.features)

        if filters.cores_min is not None:
            builder.add_condition(Features.cores >= filters.cores_min)
        if filters.cores_max is not None:
            builder.add_condition(Features.cores <= filters.cores_max)
        if filters.core_frequency_min is not None:
            builder.add_condition(Features.core_frequency >= filters.core_frequency_min)
        if filters.core_frequency_max is not None:
            builder.add_condition(Features.core_frequency <= filters.core_frequency_max)
        if filters.ram_min is not None:
            builder.add_condition(Features.ram >= filters.ram_min)
        if filters.ram_max is not None:
            builder.add_condition(Features.ram <= filters.ram_max)
        if filters.ram_type is not None:
            builder.add_condition(Features.ram_type == filters.ram_type)
        if filters.disk_min is not None:
            builder.add_condition(Features.disk >= filters.disk_min)
        if filters.disk_max is not None:
            builder.add_condition(Features.disk <= filters.disk_max)
        if filters.disk_type is not None:
            builder.add_condition(Features.disk_type == filters.disk_type)
        if filters.network_speed_min is not None:
            builder.add_condition(Features.network_speed >= filters.network_speed_min)
        if filters.network_limit_min is not None:
            builder.add_condition(Features.network_limit >= filters.network_limit_min)
        if filters.location is not None:
            builder.add_condition(Features.location.in_(filters.location))

        if filters.price_min is not None:
            builder.add_condition(PricingPlan.price >= filters.price_min)
        if filters.price_max is not None:
            builder.add_condition(PricingPlan.price <= filters.price_max)
        if filters.server_type is not None:
            builder.add_condition(PricingPlan.server_type == filters.server_type)
        if filters.billing_cycle is not None:
            builder.add_condition(PricingPlan.billing_cycle == filters.billing_cycle)
        if filters.provider_id is not None:
            builder.add_condition(PricingPlan.provider_id == filters.provider_id)

        if filters.min_rating is not None:
            stmt = stmt.join(PricingPlan.provider)
            builder.add_condition(Provider.rating >= filters.min_rating)

        conditions = builder.build()
        if conditions is not None:
            stmt = stmt.where(conditions)

        if filters.sort_by:
            sort_column = getattr(PricingPlan, filters.sort_by, None)
            if sort_column is not None:
                sort_column = sort_column.desc() if filters.sort_order == 'desc' else sort_column.asc()
                stmt = stmt.order_by(sort_column)

        stmt = stmt.offset(filters.skip).limit(filters.limit)

        result = await self._session.execute(stmt)
        return result.scalars().unique().all()


    async def update(self, plan_id: int | UUID, pricing_plan: PricingPlan):
        pass

    async def delete(self, plan_id: int | UUID) -> PricingPlan:
        stmt = delete(PricingPlan).where(PricingPlan.id == plan_id).returning(PricingPlan)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.unique().scalars().first()

