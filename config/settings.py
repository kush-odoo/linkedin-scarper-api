import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Application Config
    APP_NAME: str = "LinkedIn Voyager Scraper API"
    ENV: str = Field(default="production", alias="ENVIRONMENT")
    PORT: int = Field(default=8000, alias="PORT")
    WORKERS: int = Field(default=4, alias="WORKERS")
    
    # Security Auth
    API_AUTH_TOKEN: str = Field(..., alias="API_AUTH_TOKEN")
    
    # LinkedIn Session Credentials
    LINKEDIN_LI_AT: str = Field(..., alias="LINKEDIN_LI_AT")
    LINKEDIN_JSESSIONID: str = Field(..., alias="LINKEDIN_JSESSIONID")
    
    # Proxy Configuration (Optional)
    PROXY_DSN: str | None = Field(default=None, alias="PROXY_DSN")
    
    # Concurrency Safeguards
    MAX_CONCURRENT_REQUESTS: int = Field(default=30, alias="MAX_CONCURRENT_REQUESTS")
    REQUEST_TIMEOUT_SECONDS: float = Field(default=15.0, alias="REQUEST_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
