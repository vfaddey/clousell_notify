from datetime import datetime

from pydantic import BaseModel, UUID4, Field, condecimal

from src.schemas.pricing_plan import PricingPlanOut
from src.schemas.user import UserOut


class ReviewAdd(BaseModel):
    rating: int
    comment: str = Field(..., max_length=300)
    user_id: UUID4
    provider_id: UUID4
    pricing_plan_id: UUID4

    class Config:
        from_attributes = True

class ReviewOut(ReviewAdd):
    id: UUID4
    user: UserOut

    created_at: datetime


class ProviderAdd(BaseModel):
    name: str
    logo_url: str
    website_url: str
    sla_details: str

    class Config:
        from_attributes = True


class ProviderOut(ProviderAdd):
    id: UUID4
    rating: condecimal()
    created_at: datetime
    updated_at: datetime

    pricing_plans: list[PricingPlanOut]
    reviews: list[ReviewOut]