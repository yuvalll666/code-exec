import asyncio
import os
import tempfile
import logging
import uuid
from requests.exceptions import ReadTimeout, ConnectionError
from shared.core.config import settings
from services.worker.docker_utils import get_docker_client

logger = logging.getLogger(__name__)
client = get_docker_client()
semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_CONTAINERS)

async def execute_python_code(code: str):
    """
    Primary Entry Point: Handles Request ID generation and Queueing logic.
    """
    req_id = str(uuid.uuid4())[:8]

    logger.info(f"[{req_id}] Request received. Waiting in queue...")
   
    async with semaphore:
        logger.info(f"[{req_id}] Slot acquired! Starting execution...")
        
        # Await the actual container logic.
        stdout, stderr = await run_container_job(code, req_id)
        
        logger.info(f"[{req_id}] Execution finished. Slot freed.")
        
        return stdout, stderr, req_id

async def run_container_job(code: str, req_id: str):
    """
    Sandbox Logic: Manages temporary files and Docker lifecycle.
    """
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "script.py")
        with open(file_path, "w") as f:
            f.write(code)

        def docker_run():
            container = None
            
            try:
                volumes = {temp_dir: {'bind': '/app', 'mode': 'ro'}}
                logger.info(f"[{req_id}] 🐳 Docker: Creating container...")

                container = client.containers.run(
                    image=settings.DOCKER_IMAGE,
                    command=["python", "/app/script.py"],
                    volumes=volumes,
                    detach=True,
                    stdout=True,
                    stderr=True,
                    user=settings.CONTAINER_USER,
                    security_opt=["no-new-privileges"],
                    network_disabled=settings.NETWORK_DISABLED,
                    mem_limit=settings.CONTAINER_MEM_LIMIT,
                    storage_opt={"size": f"{settings.CONTAINER_STORAGE_LIMIT_MB}M"},
                    pids_limit=settings.CONTAINER_PIDS_LIMIT
                    # TODO: Add CPU limit 
                )
                
                try:
                    container.wait(timeout=settings.CONTAINER_TIMEOUT)
                except (ReadTimeout, ConnectionError):
                    logger.warning(f"[{req_id}] Docker: TIMEOUT reached. Killing container...")
                    container.kill()
                    return "", f"Error: Execution timed out ({settings.CONTAINER_TIMEOUT}s limit)."

                stdout = container.logs(stdout=True, stderr=False).decode("utf-8")
                stderr = container.logs(stdout=False, stderr=True).decode("utf-8")
                return stdout, stderr
            except Exception as e:
                logger.error(f"[{req_id}] System Error: {str(e)}")
                return "", f"System Error: {str(e)}"
            finally:
                if container:
                    try:
                        container.remove(force=True)
                        logger.info(f"[{req_id}] Docker: Container removed.")
                    except:
                        pass

        return await asyncio.to_thread(docker_run)