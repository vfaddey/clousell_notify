from datetime import datetime
from typing import Optional

from pydantic import BaseModel, UUID4


class TemplateCreate(BaseModel):
    name: str
    required_fields: Optional[str] = ''
    subject: str
    body: str

    class Config:
        from_attributes = True


class TemplateOut(TemplateCreate):
    id: UUID4

    created_at: datetime
    updated_at: datetime
