from typing import List, Union
from pydantic import AnyHttpUrl, BaseSettings, validator

class Settings(BaseSettings):
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    MONGODB_URL: str
    JWT_SECRET_KEY: str
    JWT_SIGNATURE_ALGORITHM: str
    JWT_TOKEN_EXPIRE_MINUTES: int
    REDIS_CACHE_HOSTNAME: str
    REDIS_CACHE_PORT: int
    REDIS_CACHE_PASSWORD: str

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
