
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime, ForeignKey, Numeric, Uuid, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BillingCyclePayment(Base):
    __tablename__ = "billing_cycle_payments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    billing_cycle_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("billing_cycles.id"), nullable=False
    )
    paycheck_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("paychecks.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
