import enum
import uuid
from datetime import datetime

from sqlalchemy import (Column,
                        UUID,
                        Enum,
                        String, Boolean, ForeignKey, DateTime, JSON)
from sqlalchemy.orm import relationship

from src.db.database import Base


class NotificationType(enum.Enum):
    EMAIL = "email"
    SITE = "site"


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    user_id = Column(UUID(as_uuid=True), nullable=False)
    email = Column(String, nullable=True)
    type = Column(Enum(NotificationType), nullable=False)
    viewed = Column(Boolean, nullable=False, default=False)

    title = Column(String, nullable=True, default='')
    message = Column(String, nullable=True, default='')

    template_id = Column(UUID(as_uuid=True), ForeignKey('templates.id'), nullable=True)
    template = relationship("Template")

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    extra_data = Column(JSON, nullable=True)

