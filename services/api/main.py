from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import uvicorn
from fastapi import Depends, FastAPI
from datetime import datetime
from services.api.models.schemas import CodeRequest, CodeResponse
from shared.core.logging_config import setup_logging
from sqlalchemy import create_engine, text
from shared.core.config import settings
from shared.db.database import get_db
from services.api.routes import job

setup_logging()

app = FastAPI()

engine = create_engine(settings.DATABASE_URL)

print(engine)

@app.get("/health/db")
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

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
    
app.include_router(job.router)

@app.post("/execute", response_model=CodeResponse)
async def run_code(payload: CodeRequest):
    return {
        "message": "run code"
    }
   
   
@app.get("{catchall:path}")
def check_all():
    return {
        "catch_all": "all"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)