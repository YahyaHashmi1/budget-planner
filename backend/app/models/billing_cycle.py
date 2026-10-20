
import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    DateTime, Enum as SQLEnum, ForeignKey,
    Numeric, Uuid, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BillingCycleStatus(str, Enum):
    FIRST_HALF_PAID = "FIRST_HALF_PAID"
    COMPLETE = "COMPLETE"


class BillingCycle(Base):
    __tablename__ = "billing_cycles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("expense_categories.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    first_pay_period_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("paychecks.id"), nullable=False
    )
    second_pay_period_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("paychecks.id"), nullable=True
    )
    status: Mapped[BillingCycleStatus] = mapped_column(
        SQLEnum(BillingCycleStatus, name="billing_cycle_status"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
