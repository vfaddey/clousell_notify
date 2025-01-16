import uuid

from sqlalchemy import Column, UUID

from src.db.database import Base


class Admin(Base):
    __tablename__ = 'admin'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4())
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)