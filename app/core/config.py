import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "HUBB ONE - Assist SaaS"
    PROJECT_VERSION: str = "1.0.0"
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    POSTGRES_HOST: str = os.environ.get("PGHOST", "localhost")
    POSTGRES_PORT: str = os.environ.get("PGPORT", "5432")
    POSTGRES_USER: str = os.environ.get("PGUSER", "postgres")
    POSTGRES_PASSWORD: str = os.environ.get("PGPASSWORD", "postgres")
    POSTGRES_DB: str = os.environ.get("PGDATABASE", "hubb_one_assist")
    DATABASE_URL: Optional[PostgresDsn] = os.environ.get("DATABASE_URL")
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            port=values.data.get("POSTGRES_PORT"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )
    
    # JWT
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "a_super_secret_key_you_should_change_in_production")
    JWT_ALGORITHM: str = "HS256"
    # 30 minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        case_sensitive = True


settings = Settings()
