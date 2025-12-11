from uuid import UUID
from datetime import date

from pydantic import BaseModel


class UserRecord(BaseModel):
    id: UUID
    name: str | None = None
    country: str | None = None  # RU, US, DE
    city: str | None = None
    age: int | None = None  # 10-100
    gender: str | None = None  # male, female
    email: str | None = None  # email type
    status: str | None = None  # new, active, deleted
    value: float | None = None  # 0-1000
    register_date: date | None = None
