import enum
from datetime import datetime

from sqlalchemy import UUID, Column, String, Boolean, Enum, DateTime

from sqlalchemy import DECIMAL
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import relationship

from src.db.database import Base


class AccountType(enum.Enum):
    PHYSICAL = "physical"
    COMPANY = "company"


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(VARCHAR(70), unique=True, nullable=False)
    email_confirmed = Column(Boolean, default=False)
    account_type = Column(Enum(AccountType), default=AccountType.PHYSICAL)
    balance = Column(DECIMAL, nullable=False, default=0)
    is_admin = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.now)

    reviews = relationship('Review', back_populates='user')

