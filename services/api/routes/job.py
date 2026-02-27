from fastapi import status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from services.api.models.schemas import CodeRequest, CodeResponse
from shared.db.database import get_db
from shared.db.models import CodeJob
from uuid import uuid4

router = APIRouter()

@router.post("/job", response_model=CodeResponse)
async def create_job(payload: CodeRequest, db: Session = Depends(get_db)):
    job_id = str(uuid4())
    
    new_job = CodeJob(
        id=job_id, 
        code=payload.code
    )
    
    try:
        db.add(new_job)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save job to database."
        )
    
    return {"job_id": job_id}