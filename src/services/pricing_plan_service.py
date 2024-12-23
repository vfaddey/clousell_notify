from typing import List
from uuid import UUID

from src.exceptions.pricing_plan import PlanInsertFailed, FailedToCreatePlan, PricingPlanNotFound
from src.exceptions.provider import ProviderNotFound
from src.models import Features, PricingPlan
from src.repositories.pricing_plan_repository import PricingPlanRepository
from src.repositories.provider_repository import ProviderRepository
from src.schemas.pricing_plan import PricingPlanAdd, PricingPlanOut, PricingPlanFilter


class PricingPlanService:
    def __init__(self,
                 pricing_plan_repository: PricingPlanRepository,
                 provider_repository: ProviderRepository):
        self.__provider_repository = provider_repository
        self.__pricing_plan_repository = pricing_plan_repository

    async def add(self, pricing_plan: PricingPlanAdd) -> PricingPlanOut:
        try:
            provider = await self.__provider_repository.get(pricing_plan.provider_id)
            if not provider:
                raise ProviderNotFound(f'No provider with id {pricing_plan.provider_id}')
            features = Features(**pricing_plan.features.model_dump())
            plan_to_insert = PricingPlan(name=pricing_plan.name,
                                         description=pricing_plan.description,
                                         price=pricing_plan.price,
                                         server_type=pricing_plan.server_type,
                                         provider_id=provider.id,
                                         billing_cycle=pricing_plan.billing_cycle,
                                         additional_info=pricing_plan.additional_info)
            plan_to_insert.features = features
            inserted = await self.__pricing_plan_repository.create(plan_to_insert)
        except PlanInsertFailed as e:
            raise FailedToCreatePlan(str(e))
        return PricingPlanOut.from_orm(inserted)

    async def get(self, plan_id: UUID) -> PricingPlanOut:
        plan = await self.__pricing_plan_repository.get(plan_id)
        if not plan:
            raise PricingPlanNotFound(f'No pricing plan with id {plan_id}')
        return PricingPlanOut.from_orm(plan)

    async def get_all(self) -> List[PricingPlanOut]:
        plans = await self.__pricing_plan_repository.get_all()
        return [PricingPlanOut.from_orm(p) for p in plans]

    async def get_by_filter(self, filters: PricingPlanFilter) -> list[PricingPlanOut]:
        plans = await self.__pricing_plan_repository.get_by_filter(filters)
        return [PricingPlanOut.from_orm(p) for p in plans]

    async def delete(self, provider_id: int) -> PricingPlanOut:
        provider = await self.__provider_repository.delete(provider_id)
        if not provider:
            raise ProviderNotFound(f'No provider with id {provider_id}')
        return PricingPlanOut.from_orm(provider)
