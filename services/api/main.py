import uvicorn
from fastapi import FastAPI
from shared.core.logging_config import setup_logging
from services.api.routes import job
from services.api.routes import health

setup_logging()

app = FastAPI()

app.include_router(health.router)
app.include_router(job.router)
   
@app.get("{catchall:path}")
def check_all():
    return {
        "catch_all": "all"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)