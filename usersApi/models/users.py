from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


class BaseUser(BaseModel):
    username: str
    email: str


class UnregisteredUser(BaseUser):
    password: str


class RegisteredUser(BaseUser):
    id: int
    register_date: datetime


class UpdateUser(BaseUser):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
