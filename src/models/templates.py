import uuid
from datetime import datetime

from sqlalchemy import (Column,
                        UUID,
                        String,
                        DateTime)
from sqlalchemy.orm import relationship

from src.db.database import Base


class Template(Base):
    __tablename__ = 'templates'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    required_fields = Column(String, nullable=False, default='')

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    notifications = relationship("Notification", cascade="all, delete-orphan", back_populates="template")
