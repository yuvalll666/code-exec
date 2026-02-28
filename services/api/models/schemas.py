from typing import Optional
from pydantic import BaseModel, Field, field_validator

class CodeRequest(BaseModel):
    code: str = Field(
        ...,
        min_length=1,
        max_length=100000,
        description="The Python code to execute in the sandbox.",
        examples=["print('Hello from the container!')"]
    )

    @field_validator('code')  
    @classmethod
    def code_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Code cannot be empty or just whitespace')
        return v

    
class JobStatusResponse(BaseModel):
    id: str = Field(..., description="The job ID.")
    status: str = Field(..., description="The current status: pending, processing, completed, or failed.")
    stdout: Optional[str] = Field(None, description="The standard output from the execution.")
    stderr: Optional[str] = Field(None, description="The error output from the execution.")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "stdout": "4\n",
                "stderr": "",
            }
        }

        
class SetJobResponse(BaseModel):
    job_id: str = Field(..., description="The standard output from the execution.")