from fastapi import APIRouter
from app.models.schemas import CodeRequest, CodeResponse
from app.services.docker_service import execute_python_code

router = APIRouter()

@router.post("/execute", response_model=CodeResponse)
async def run_code(payload: CodeRequest):
    stdout, stderr, req_id = await execute_python_code(payload.code)
    
    return CodeResponse(
        stdout=stdout,
        stderr=stderr,
        request_id=req_id
    )