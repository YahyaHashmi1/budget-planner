from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal
from app.routers import paychecks, users, billing_cycles, billing_cycle_payments, expense_categories, expense_items
from app.dependencies import get_db

app = FastAPI(
    title="Paycheck Tracker API",
    description="API for tracking paychecks, expenses, and recurring bills.",
    version="0.1.0",
)

# Allow the local Vite frontend to make requests to the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Paycheck Tracker API is running"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        # Log the exception in a fuller implementation.
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from exc

app.include_router(paychecks.router)
app.include_router(users.router)
app.include_router(expense_categories.router)
app.include_router(expense_items.router)
app.include_router(billing_cycles.router)
app.include_router(billing_cycle_payments.router)

