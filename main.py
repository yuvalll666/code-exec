import uvicorn
from fastapi import FastAPI
from datetime import datetime
from app.routes import execution
from app.core.logging_config import setup_logging
from app.utils.docker_utils import get_docker_client

setup_logging()
# Fail fast if Docker is unreachable
get_docker_client()  # triggers init/check; raises if Docker is down

app = FastAPI()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

app.include_router(execution.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)