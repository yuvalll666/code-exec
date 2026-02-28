from fastapi import status
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from shared.db.models import CodeJob
from uuid import uuid4
from shared.queue.redis_client import r
import logging

logger = logging.getLogger(__name__)

def create_job(code: str, db: Session):
    job_id = str(uuid4())
    
    new_job = CodeJob(
        id=job_id, 
        code=code
    )
    
    try:
        db.add(new_job)
        db.commit()
        r.rpush("job_queue", job_id)
        logger.info(f"Job {job_id} successfully queued")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create job in DB or Redis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save job to database."
        )
    
    return {"job_id": job_id}

def get_job_status(job_id: str, db: Session):
    job = db.query(CodeJob).filter(CodeJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job
    
    