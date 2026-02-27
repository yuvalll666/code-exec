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

class CodeResponse(BaseModel):
    job_id: str = Field(..., description="The standard output from the execution.")