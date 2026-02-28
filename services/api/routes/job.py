from fastapi import APIRouter, Depends
from services.api.models.schemas import CodeRequest, JobStatusResponse, SetJobResponse
from services.api.services.job_service import create_job, get_job_status
from sqlalchemy.orm import Session
from shared.db.database import get_db

router = APIRouter()

@router.post("/job", response_model=SetJobResponse)
async def new_job_request(payload: CodeRequest, db: Session = Depends(get_db)):
    return create_job(code=payload.code, db=db)

@router.get("/job/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str, db: Session = Depends(get_db)):
    return get_job_status(job_id=job_id, db=db)