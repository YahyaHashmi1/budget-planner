from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


# Defines the fields the client must provide when creating a user.
class UserCreate(BaseModel):
    email: EmailStr  # Validates that the input looks like an email address.


# Defines the fields the API returns after creating or retrieving a user.
class UserRead(BaseModel):
    # Allows Pydantic to read values directly from a SQLAlchemy model.
    model_config = ConfigDict(from_attributes=True)

    id: UUID  # The database-generated user's unique identifier.
    email: EmailStr  # The user's email address.
    created_at: datetime  # When the database record was created.
