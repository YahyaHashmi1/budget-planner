from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.expense_category import ExpenseCategory
from app.models.user import User
from app.schemas.expense_category import (
    ExpenseCategoryCreate,
    ExpenseCategoryRead,
    ExpenseCategoryUpdate,
)

router = APIRouter(prefix="/expense-categories", tags=["Expense Categories"])


@router.post("", response_model=ExpenseCategoryRead, status_code=201)
def create_category(
    data: ExpenseCategoryCreate,
    db: Session = Depends(get_db),
):
    # Confirm that the owner exists before creating the category.
    if db.get(User, data.user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Create the category using validated request data.
    category = ExpenseCategory(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get("", response_model=list[ExpenseCategoryRead])
def list_categories(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    # Return only categories belonging to the requested user.
    return (
        db.query(ExpenseCategory)
        .filter(ExpenseCategory.user_id == user_id)
        .order_by(ExpenseCategory.name)
        .all()
    )


@router.patch("/{category_id}", response_model=ExpenseCategoryRead)
def update_category(
    category_id: UUID,
    data: ExpenseCategoryUpdate,
    db: Session = Depends(get_db),
):
    # Find the category that will be updated.
    category = db.get(ExpenseCategory, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Only update fields the client actually supplied.
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", response_model=ExpenseCategoryRead)
def deactivate_category(
    category_id: UUID,
    db: Session = Depends(get_db),
):
    # Preserve historical expenses by deactivating instead of deleting.
    category = db.get(ExpenseCategory, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    category.active = False
    db.commit()
    db.refresh(category)

    return category
