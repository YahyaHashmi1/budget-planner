
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExpenseItemCreate(BaseModel):
    # Category and paycheck this expense belongs to.
    category_id: UUID
    paycheck_id: UUID
    
    name: str = Field(min_length=1, max_length=150)

    # Require a positive amount with at most two decimal places.
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)

    # Date the purchase happened; defaults to today's date.
    spent_on: date = Field(default_factory=date.today)


class ExpenseItemRead(BaseModel):
    # Convert the database model into this response format.
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: UUID
    paycheck_id: UUID
    name: str
    amount: Decimal
    spent_on: date
    created_at: datetime
