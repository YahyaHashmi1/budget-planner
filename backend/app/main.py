
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.routers import paychecks
from app.routers import users

app = FastAPI(
    title="Paycheck Tracker API",
    description="API for tracking paychecks, expenses, and recurring bills.",
    version="0.1.0",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
