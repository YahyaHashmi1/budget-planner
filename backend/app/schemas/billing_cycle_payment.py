from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BillingCyclePaymentRead(BaseModel):
    # Return an allocation as a normal API response.
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    billing_cycle_id: UUID
    paycheck_id: UUID
    amount: Decimal
    created_at: datetime
