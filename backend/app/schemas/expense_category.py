from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Reuse the enum defined in the SQLAlchemy model.
from app.models.expense_category import CategoryType


class ExpenseCategoryCreate(BaseModel):
    user_id: UUID
    name: str = Field(min_length=1, max_length=100)

    # Optional spending limit; None means no budget limit is set.
    budget: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )

    # Determines whether the category is recurring.
    type: CategoryType

    # New categories are active by default.
    active: bool = True


class ExpenseCategoryUpdate(BaseModel):
    # All fields are optional so clients can update only what changed.
    name: str | None = Field(default=None, min_length=1, max_length=100)
    budget: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    type: CategoryType | None = None
    active: bool | None = None


class ExpenseCategoryRead(BaseModel):
    # Allows Pydantic to serialize SQLAlchemy model objects.
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    budget: Decimal | None
    type: CategoryType
    active: bool
