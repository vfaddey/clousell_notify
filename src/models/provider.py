import enum
import uuid
from datetime import datetime

from sqlalchemy import UUID, Column, String, DECIMAL, ForeignKey, Enum, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from src.db.database import Base


class Provider(Base):
    __tablename__ = 'providers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    name = Column(String, nullable=False, unique=True)
    logo_url = Column(String, nullable=False)
    website_url = Column(String, nullable=False)
    sla_details = Column(String, nullable=False)
    rating = Column(DECIMAL, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    pricing_plans = relationship('PricingPlan', back_populates='provider',cascade='all, delete', lazy='joined')
    reviews = relationship('Review', cascade='all, delete', back_populates='provider', lazy='joined')


class BillingCycle(str, enum.Enum):
    MONTHLY = 'monthly'
    ANNUALLY = 'annually'


class ServerType(str, enum.Enum):
    VIRTUAL = 'virtual'
    DEDICATED = 'dedicated'


class PricingPlan(Base):
    __tablename__ = 'pricing_plans'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    name = Column(String, nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey('providers.id'), nullable=False)
    description = Column(String(255), nullable=False, default='')
    price = Column(DECIMAL, nullable=False)
    billing_cycle = Column(Enum(BillingCycle, enum=BillingCycle), nullable=False)
    server_type = Column(Enum(ServerType), nullable=False)
    features_id = Column(UUID(as_uuid=True), ForeignKey('features.id'), nullable=False)
    additional_info = Column(JSON, default={})

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    provider = relationship('Provider', back_populates='pricing_plans')
    features = relationship('Features', cascade='all, delete', lazy='joined')
    reviews = relationship('Review', cascade='all, delete')


class RAMType(str, enum.Enum):
    DDR3 = 'DDR3'
    DDR4 = 'DDR4'
    DDR5 = 'DDR5'


class DiskType(str, enum.Enum):
    HDD = 'HDD'
    SSD = 'SSD'
    NVME = 'NVME'


class Features(Base):
    __tablename__ = 'features'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    processor_name = Column(String(50), default='')
    cores = Column(Integer, nullable=False)
    core_frequency = Column(DECIMAL)

    ram = Column(Integer, nullable=False)
    ram_type = Column(Enum(RAMType), nullable=False)

    disk = Column(DECIMAL, nullable=False)
    disk_type = Column(Enum(DiskType), default=DiskType.SSD)
    network_speed = Column(DECIMAL)
    network_limit = Column(Integer)
    location = Column(String(40), default='')

    pricing_plan = relationship('PricingPlan', back_populates='features', lazy='joined')


class ReviewStatus(str, enum.Enum):
    PENDING = 'pending'
    REJECTED = 'rejected'
    APPROVED = 'approved'


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)

    rating = Column(DECIMAL, nullable=False, default=0)
    comment = Column(String(300), nullable=False)
    status = Column(Enum(ReviewStatus), nullable=False, default=ReviewStatus.PENDING)

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey('providers.id'), nullable=False)
    pricing_plan_id = Column(UUID(as_uuid=True), ForeignKey('pricing_plans.id'), nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='reviews')
    provider = relationship('Provider', back_populates='reviews')
    pricing_plan = relationship('PricingPlan', back_populates='reviews')

