from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.expense_category import CategoryType, ExpenseCategory
from app.models.expense_item import ExpenseItem
from app.models.paycheck import Paycheck
from app.schemas.expense_item import ExpenseItemCreate, ExpenseItemRead

router = APIRouter(prefix="/expense-items", tags=["Expense Items"])


@router.post("", response_model=ExpenseItemRead, status_code=201)
def create_expense_item(
    data: ExpenseItemCreate,
    db: Session = Depends(get_db),
):
    # Make sure both referenced records exist.
    category = db.get(ExpenseCategory, data.category_id)
    paycheck = db.get(Paycheck, data.paycheck_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if paycheck is None:
        raise HTTPException(status_code=404, detail="Paycheck not found")

    # Prevent spending from being recorded under an inactive category.
    if not category.active:
        raise HTTPException(status_code=400, detail="Category is inactive")

    # Recurring bills must use billing cycles, not ordinary expense items.
    if category.type != CategoryType.VARIABLE_NON_RECURRING:
        raise HTTPException(
            status_code=400,
            detail="Use billing cycles for recurring categories",
        )

    # Ensure the category and paycheck belong to the same user.
    if category.user_id != paycheck.user_id:
        raise HTTPException(
            status_code=400,
            detail="Category and paycheck belong to different users",
        )

    # Create and save the expense item.
    item = ExpenseItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get("", response_model=list[ExpenseItemRead])
def list_expense_items(
    paycheck_id: UUID,
    db: Session = Depends(get_db),
):
    # List all expense items associated with the selected paycheck.
    return (
        db.query(ExpenseItem)
        .filter(ExpenseItem.paycheck_id == paycheck_id)
        .order_by(ExpenseItem.spent_on.desc())
        .all()
    )


@router.delete("/{item_id}", status_code=204)
def delete_expense_item(
    item_id: UUID,
    db: Session = Depends(get_db),
):
    # Find the purchase the user wants to remove.
    item = db.get(ExpenseItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Expense item not found")

    # Delete the item and save the transaction.
    db.delete(item)
    db.commit()

    # A 204 response intentionally has no response body.
    return None
