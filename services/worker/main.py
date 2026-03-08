import asyncio
from shared.core.logging_config import setup_logging
import logging
from shared.db.database import SessionLocal
from shared.db.models import CodeJob, JobStatus
from shared.queue.redis_client import r
from services.worker.docker_service import execute_python_code

setup_logging()
logger = logging.getLogger("worker")

# This set keeps track of running tasks so the Garbage Collector doesn't kill them
running_tasks = set()

async def handle_individual_job(job_id: str, semaphore: asyncio.Semaphore):
    """Handles the lifecycle of a single job and releases the slot when done."""
    try:
        with SessionLocal() as db:
            job = db.query(CodeJob).filter(CodeJob.id == job_id).first()
            if not job:
                return

            job.status = JobStatus.PROCESSING
            db.commit()

            try:
                # The actual Docker execution
                stdout, stderr, req_id = await execute_python_code(job.code)
                
                job.stdout = stdout
                job.stderr = stderr
                job.status = JobStatus.FAILED if stderr else JobStatus.COMPLETED
                logger.info(f"✅ Job {job_id} ({req_id}) finished.")
            except Exception as exec_err:
                logger.error(f"Execution failed for {job_id}: {exec_err}")
                job.status = JobStatus.FAILED
                job.stderr = str(exec_err)
            
            db.commit()
    except Exception as e:
        logger.error(f"Database error for job {job_id}: {e}")
    finally:
        # 1 out, 1 in: release the slot back to the main loop
        semaphore.release()

async def process_job():
    logger.info("🚀 Worker is online. Max concurrency: 3. Waiting for jobs...")
    
    # We use a semaphore to limit how many jobs we pull from Redis
    semaphore = asyncio.Semaphore(3)

    while True:
        # Pause here if 3 jobs are already running
        await semaphore.acquire()
        
        try:
            # blpop is synchronous/blocking, so we run it in a thread 
            # so it doesn't stop the other jobs from finishing
            result = await asyncio.to_thread(r.blpop, "job_queue", 0)
            _, job_id = result
            
            logger.info(f"📥 Slot acquired. Picked up job: {job_id}")

            # Fire off the task in the background
            task = asyncio.create_task(handle_individual_job(job_id, semaphore))
            
            # Standard practice to prevent task disappearance
            running_tasks.add(task)
            task.add_done_callback(running_tasks.discard)

        except Exception as e:
            logger.error(f"Worker Loop Error: {e}")
            # If we failed to get a job, release the slot we just acquired
            semaphore.release()
            await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(process_job())
    except KeyboardInterrupt:
        logger.info("Worker shutting down gracefully...")