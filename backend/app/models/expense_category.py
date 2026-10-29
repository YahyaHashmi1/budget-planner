
import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Boolean, DateTime, Enum as SQLEnum,
    ForeignKey, Numeric, String, Uuid, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CategoryType(str, Enum):
    VARIABLE_NON_RECURRING = "VARIABLE_NON_RECURRING"
    FIXED_RECURRING = "FIXED_RECURRING"
    VARIABLE_RECURRING = "VARIABLE_RECURRING"


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    budget: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    type: Mapped[CategoryType] = mapped_column(
        SQLEnum(CategoryType, name="category_type"), nullable=False,
    )
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
