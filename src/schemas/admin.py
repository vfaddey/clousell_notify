
from pydantic import BaseModel, UUID4


class AdminSchema(BaseModel):
    id: UUID4
    user_id: UUID4

    class Config:
        from_attributes = True