from app.database import SessionLocal


def get_db():
    # Open a database session for the current request.
    db = SessionLocal()
    try:
        yield db  # Provide the session to the endpoint.
    finally:
        db.close()  # Close the session afterward.