
from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.paycheck import Paycheck
from app.schemas.paycheck import PaycheckCreate, PaycheckRead

router = APIRouter(prefix="/paychecks", tags=["Paychecks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=PaycheckRead, status_code=201)
def create_paycheck(
    paycheck_data: PaycheckCreate,
    db: Session = Depends(get_db),
):
    period_start = paycheck_data.pay_date
    period_end = period_start + timedelta(days=14)

    paycheck = Paycheck(
        user_id=paycheck_data.user_id,
        amount=paycheck_data.amount,
        pay_date=paycheck_data.pay_date,
        period_start=period_start,
        period_end=period_end,
    )

    db.add(paycheck)

    try:
        db.commit()
        db.refresh(paycheck)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create paycheck",
        )

    return paycheck


@router.get("", response_model=list[PaycheckRead])
def list_paychecks(db: Session = Depends(get_db)):
    return (
        db.query(Paycheck)
        .order_by(Paycheck.pay_date.desc())
        .all()
    )


@router.get("/{paycheck_id}", response_model=PaycheckRead)
def get_paycheck(
    paycheck_id: UUID,
    db: Session = Depends(get_db),
):
    paycheck = db.get(Paycheck, paycheck_id)

    if paycheck is None:
        raise HTTPException(
            status_code=404,
            detail="Paycheck not found",
        )

    return paycheck
