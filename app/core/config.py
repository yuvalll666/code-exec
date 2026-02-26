from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Python Code Execution Engine"
    API_V1_STR: str = "/api/v1"
    
    # Docker Resource Limits
    DOCKER_IMAGE: str = Field(default="python:3.10-slim", env="DOCKER_IMAGE")
    MAX_CONCURRENT_CONTAINERS: int = Field(default=3, env="MAX_CONCURRENT_CONTAINERS")
    CONTAINER_MEM_LIMIT: str = Field(default="128m", env="CONTAINER_MEM_LIMIT")
    CONTAINER_TIMEOUT: int = Field(default=5, env="CONTAINER_TIMEOUT")
    CONTAINER_PIDS_LIMIT: int = Field(default=50, env="CONTAINER_PIDS_LIMIT")
    CONTAINER_STORAGE_LIMIT_MB: int = Field(default=100, env="CONTAINER_STORAGE_LIMIT_MB")
    
    # Security Settings
    NETWORK_DISABLED: bool = True
    CONTAINER_USER: str = "1000:1000"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()