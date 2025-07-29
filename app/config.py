import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AWS Settings
    aws_region: str = "us-east-1"
    aws_secret_name: str = "snowflake-credentials"
    
    # Snowflake Settings (will be loaded from AWS Secrets Manager)
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    snowflake_warehouse: Optional[str] = None
    snowflake_database: Optional[str] = None
    snowflake_schema: Optional[str] = None
    snowflake_role: Optional[str] = None
    
    # API Settings
    api_title: str = "FastAPI Snowflake API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


settings = Settings()
