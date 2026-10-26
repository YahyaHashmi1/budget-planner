from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.billing_cycle import BillingCycle, BillingCycleStatus
from app.models.billing_cycle_payment import BillingCyclePayment
from app.models.expense_category import CategoryType, ExpenseCategory
from app.models.paycheck import Paycheck
from app.schemas.billing_cycle import (
    BillingCycleCreate,
    BillingCycleRead,
    BillingCycleSecondPayment,
)

router = APIRouter(prefix="/billing-cycles", tags=["Billing Cycles"])


@router.post("", response_model=BillingCycleRead, status_code=201)
def create_billing_cycle(
    data: BillingCycleCreate,
    db: Session = Depends(get_db),
):
    # Find the category and paycheck selected for the first allocation.
    category = db.get(ExpenseCategory, data.category_id)
    paycheck = db.get(Paycheck, data.paycheck_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if paycheck is None:
        raise HTTPException(status_code=404, detail="Paycheck not found")

    # Only fixed or variable recurring categories use billing cycles.
    if category.type == CategoryType.VARIABLE_NON_RECURRING:
        raise HTTPException(
            status_code=400,
            detail="This category does not use recurring billing cycles",
        )

    if not category.active:
        raise HTTPException(status_code=400, detail="Category is inactive")

    # The category and paycheck must belong to the same user.
    if category.user_id != paycheck.user_id:
        raise HTTPException(
            status_code=400,
            detail="Category and paycheck belong to different users",
        )

    # Do not allow a second cycle while the previous cycle is still open.
    open_cycle = (
        db.query(BillingCycle)
        .filter(
            BillingCycle.category_id == category.id,
            BillingCycle.status == BillingCycleStatus.FIRST_HALF_PAID,
        )
        .first()
    )
    if open_cycle is not None:
        raise HTTPException(
            status_code=409,
            detail="This category already has an open billing cycle",
        )

    # Round the first half to cents; the second half receives the remainder.
    first_amount = (data.total_amount / Decimal("2")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Start the cycle as incomplete until the second allocation is recorded.
    cycle = BillingCycle(
        category_id=category.id,
        total_amount=data.total_amount,
        status=BillingCycleStatus.FIRST_HALF_PAID,
    )
    db.add(cycle)
    db.flush()  # Generate cycle.id before creating its payment record.

    # Record the first allocation in the source-of-truth payments table.
    first_payment = BillingCyclePayment(
        billing_cycle_id=cycle.id,
        paycheck_id=paycheck.id,
        amount=first_amount,
    )
    db.add(first_payment)

    try:
        # Save the cycle and its first payment in one transaction.
        db.commit()
        db.refresh(cycle)
    except IntegrityError as exc:
        # A concurrent request may have created an open cycle first.
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not create cycle; check for an existing open cycle",
        ) from exc

    return cycle


@router.post(
    "/{cycle_id}/second-payment",
    response_model=BillingCycleRead,
)
def add_second_payment(
    cycle_id: UUID,
    data: BillingCycleSecondPayment,
    db: Session = Depends(get_db),
):
    # Find the cycle and the paycheck for the second allocation.
    cycle = db.get(BillingCycle, cycle_id)
    paycheck = db.get(Paycheck, data.paycheck_id)

    if cycle is None:
        raise HTTPException(status_code=404, detail="Billing cycle not found")
    if paycheck is None:
        raise HTTPException(status_code=404, detail="Paycheck not found")

    # Only cycles awaiting their second half can be completed.
    if cycle.status != BillingCycleStatus.FIRST_HALF_PAID:
        raise HTTPException(
            status_code=409,
            detail="This billing cycle is already complete",
        )

    # Verify that this paycheck belongs to the category's owner.
    category = db.get(ExpenseCategory, cycle.category_id)
    if category is None or category.user_id != paycheck.user_id:
        raise HTTPException(
            status_code=400,
            detail="Paycheck does not belong to the category owner",
        )

    # Find the first allocation; it determines the remaining balance.
    first_payment = (
        db.query(BillingCyclePayment)
        .filter(BillingCyclePayment.billing_cycle_id == cycle.id)
        .first()
    )
    if first_payment is None:
        raise HTTPException(
            status_code=409,
            detail="First payment is missing; cycle cannot be completed",
        )

    # A cycle must use a different paycheck for its second allocation.
    if first_payment.paycheck_id == paycheck.id:
        raise HTTPException(
            status_code=400,
            detail="Choose a different paycheck for the second allocation",
        )

    # The remaining amount ensures both allocations add up exactly.
    remaining_amount = cycle.total_amount - first_payment.amount

    # Create the second payment and complete the cycle together.
    second_payment = BillingCyclePayment(
        billing_cycle_id=cycle.id,
        paycheck_id=paycheck.id,
        amount=remaining_amount,
    )
    db.add(second_payment)

    cycle.status = BillingCycleStatus.COMPLETE
    cycle.completed_at = datetime.now(timezone.utc)

    try:
        # Save the second payment and status change atomically.
        db.commit()
        db.refresh(cycle)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not save the second payment",
        ) from exc

    return cycle


@router.get("", response_model=list[BillingCycleRead])
def list_billing_cycles(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    # Find cycles through their categories, which identify the owner.
    return (
        db.query(BillingCycle)
        .join(
            ExpenseCategory,
            BillingCycle.category_id == ExpenseCategory.id,
        )
        .filter(ExpenseCategory.user_id == user_id)
        .order_by(BillingCycle.created_at.desc())
        .all()
    )
