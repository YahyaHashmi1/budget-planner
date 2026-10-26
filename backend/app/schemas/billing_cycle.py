
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.billing_cycle import BillingCycleStatus


class BillingCycleCreate(BaseModel):
    # Category and paycheck used to begin allocating this bill.
    category_id: UUID
    paycheck_id: UUID

    # Full bill amount, not just the first-half allocation.
    total_amount: Decimal = Field(
        gt=0, max_digits=10, decimal_places=2
    )


class BillingCycleSecondPayment(BaseModel):
    # Paycheck receiving the second-half allocation.
    paycheck_id: UUID


class BillingCycleRead(BaseModel):
    # Serialize SQLAlchemy billing-cycle objects.
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: UUID
    total_amount: Decimal
    status: BillingCycleStatus
    created_at: datetime
    completed_at: datetime | None
