from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaycheckCreate(BaseModel):
    user_id: UUID
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    pay_date: date


class PaycheckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    amount: Decimal
    pay_date: date
    period_start: date
    period_end: date
