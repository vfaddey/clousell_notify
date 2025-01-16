from datetime import datetime
from typing import Optional

from pydantic import BaseModel, UUID4, EmailStr

from src.models import NotificationType


class NotificationCreate(BaseModel):
    user_id: UUID4
    type: NotificationType
    title: Optional[str] = ''
    message: Optional[str] = ''
    email: Optional[EmailStr] = None
    template_id: Optional[UUID4] = None

    extra_data: Optional[dict] = {}


class NotificationOut(BaseModel):
    id: UUID4
    user_id: UUID4
    viewed: bool
    title: Optional[str] = ''
    message: Optional[str] = ''
    created_at: datetime

    class Config:
        from_attributes = True
