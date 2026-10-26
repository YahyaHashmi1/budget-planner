from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.billing_cycle import BillingCycle
from app.models.billing_cycle_payment import BillingCyclePayment
from app.schemas.billing_cycle_payment import BillingCyclePaymentRead

router = APIRouter(
    prefix="/billing-cycle-payments",
    tags=["Billing Cycle Payments"],
)


@router.get("", response_model=list[BillingCyclePaymentRead])
def list_cycle_payments(
    billing_cycle_id: UUID,
    db: Session = Depends(get_db),
):
    # Confirm that the requested cycle exists.
    cycle = db.get(BillingCycle, billing_cycle_id)
    if cycle is None:
        raise HTTPException(status_code=404, detail="Billing cycle not found")

    # Return the paycheck allocations recorded for this cycle.
    return (
        db.query(BillingCyclePayment)
        .filter(BillingCyclePayment.billing_cycle_id == billing_cycle_id)
        .order_by(BillingCyclePayment.created_at)
        .all()
    )
