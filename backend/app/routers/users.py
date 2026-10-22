
# backend/app/routers/users.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserRead


# Groups user-related endpoints under the /users URL prefix.
router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    # Opens a database session for this request.
    db = SessionLocal()
    try:
        yield db  # Makes the session available to the endpoint.
    finally:
        db.close()  # Always closes the session when the request finishes.


@router.post("", response_model=UserRead, status_code=201)
def create_user(
    user_data: UserCreate,  # FastAPI validates the request using UserCreate.
    db: Session = Depends(get_db),  # Injects a database session.
):
    # Build a SQLAlchemy object from the validated request data.
    user = User(email=str(user_data.email))

    # Stage the new user for insertion into the database.
    db.add(user)

    try:
        # Save the record and commit the transaction.
        db.commit()

        # Load database-generated values, such as ID and created_at.
        db.refresh(user)
    except IntegrityError as exc:
        # Undo the failed transaction, for example if the email already exists.
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A user with this email already exists",
        ) from exc

    # FastAPI converts the SQLAlchemy object to the UserRead response.
    return user


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: UUID,  # FastAPI validates that the path value is a UUID.
    db: Session = Depends(get_db),  # Injects a database session.
):
    # Look up the user by its primary key.
    user = db.get(User, user_id)

    # Return a 404 if the database has no matching user.
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Return the user in the UserRead response format.
    return user
