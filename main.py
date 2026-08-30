import re
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.settings import settings
from models.schema import ScrapeRequest, ProfileResponse
from engine.transport import voyager_transport

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("api_main")

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != settings.API_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authorization bearer token."
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize HTTP connection pool
    voyager_transport.start()
    yield
    # Shutdown: Close HTTP connections cleanly
    await voyager_transport.stop()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="High-throughput reverse-engineered LinkedIn extraction microservice.",
    lifespan=lifespan
)

def extract_slug(url_str: str) -> str:
    pattern = r"linkedin\.com/in/([a-zA-Z0-9%_-]+)"
    match = re.search(pattern, url_str)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid LinkedIn profile URL. Example: 'https://www.linkedin.com/in/username'"
        )
    return match.group(1).rstrip('/')

@app.post(
    "/api/v1/scrape",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK
)
async def scrape_profile_endpoint(payload: ScrapeRequest):
    slug = extract_slug(str(payload.url))
    return await voyager_transport.fetch_profile(slug)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}
