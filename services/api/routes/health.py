from datetime import datetime
from pydoc import text
from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from shared.db.database import get_db

router = APIRouter()

@router.get("/health/db")
def db_health_check(db: Session = Depends(get_db)):
    try:
        # Execute a simple query to test DB connection
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {"status": "healthy"}
        else:
            return {"status": "unhealthy", "error": "Unexpected query result"}
    except SQLAlchemyError as e:
        # Catch any SQLAlchemy DB errors
        return {"status": "unhealthy", "error": str(e)}

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }