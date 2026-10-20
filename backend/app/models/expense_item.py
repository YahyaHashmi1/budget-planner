
import uuid
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    DateTime, Date, ForeignKey, Numeric, String, Uuid, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExpenseItem(Base):
    __tablename__ = "expense_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("expense_categories.id"), nullable=False
    )
    paycheck_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("paychecks.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    spent_on: Mapped[date] = mapped_column(
        Date, nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
