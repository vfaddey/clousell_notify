from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4, Field, condecimal
from src.models import RAMType, DiskType, BillingCycle, ServerType


class FeaturesAdd(BaseModel):
    processor_name: str = Field(..., max_length=50)
    cores: int
    core_frequency: Optional[condecimal()] = None
    ram: condecimal()
    ram_type: RAMType
    disk: condecimal()
    disk_type: DiskType
    network_speed: condecimal()
    network_limit: condecimal()
    location: Optional[str] = Field(default='', max_length=40)

    class Config:
        from_attributes = True

class FeaturesOut(FeaturesAdd):
    id: UUID4



class PricingPlanAdd(BaseModel):
    name: str
    provider_id: UUID4
    description: Optional[str] = Field(default='', max_length=255)
    billing_cycle: BillingCycle
    server_type: ServerType
    price: condecimal()
    features: FeaturesAdd

    class Config:
        from_attributes = True


class PricingPlanOut(PricingPlanAdd):
    id: UUID4
    features: FeaturesOut

    created_at: datetime
    updated_at: datetime


@dataclass
class PricingPlanFilter:
    cores_min: Optional[int] = Field(None, ge=1, description="Минимальное количество ядер")
    cores_max: Optional[int] = Field(None, ge=1, description="Максимальное количество ядер")
    core_frequency_min: Optional[float] = Field(None, ge=0, description="Минимальная частота ядра (ГГц)")
    core_frequency_max: Optional[float] = Field(None, ge=0, description="Максимальная частота ядра (ГГц)")
    ram_min: Optional[float] = Field(None, ge=0, description="Минимальный объем оперативной памяти (GB)")
    ram_max: Optional[float] = Field(None, ge=0, description="Максимальный объем оперативной памяти (GB)")
    ram_type: Optional[RAMType] = Field(None, description="Тип оперативной памяти")
    disk_min: Optional[float] = Field(None, ge=0, description="Минимальный объем диска (GB)")
    disk_max: Optional[float] = Field(None, ge=0, description="Максимальный объем диска (GB)")
    disk_type: Optional[DiskType] = Field(None, description="Тип диска (NVME, SSD, HDD)")
    network_speed_min: Optional[float] = Field(None, ge=0, description="Минимальная скорость сети (Mbps)")
    network_limit_min: Optional[float] = Field(None, ge=0, description="Минимальный лимит сети (GB)")
    location: Optional[list[str]] = Field(None, description="Местоположения (можно несколько)")
    price_min: Optional[float] = Field(None, ge=0, description="Минимальная цена")
    price_max: Optional[float] = Field(None, ge=0, description="Максимальная цена")
    server_type: Optional[ServerType] = Field(None, description="Тип сервера (virtual или dedicated)")
    billing_cycle: Optional[BillingCycle] = Field(None, description="Период списания")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Минимальный рейтинг")
    provider_id: Optional[UUID4] = Field(None, description='ID провайдера')
    sort_by: Optional[str] = Field(None, description="Поле для сортировки (price, rating)")
    sort_order: Optional[str] = Field('asc', description="Порядок сортировки (asc или desc)")
    skip: int = Field(0, ge=0, description="Количество пропущенных записей")
    limit: int = Field(100, ge=1, le=1000, description="Максимальное количество записей")