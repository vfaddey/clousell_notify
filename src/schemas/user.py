from black import datetime
from pydantic import BaseModel, EmailStr, condecimal
from pydantic import UUID4
from src.models import AccountType


class UserAdd(BaseModel):
    id: UUID4
    name: str
    email: EmailStr
    email_confirmed: bool
    account_type: AccountType
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserOut(UserAdd):
    balance: condecimal()
    is_admin: bool = False
