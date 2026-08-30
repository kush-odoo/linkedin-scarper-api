import random
import asyncio
import logging
from typing import Dict, Any
import httpx
from fastapi import HTTPException, status
from config.settings import settings
from engine.parser import parse_voyager_response
from models.schema import ProfileResponse

logger = logging.getLogger("voyager_transport")

class VoyagerTransportClient:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)
        self.client: httpx.AsyncClient | None = None

    def start(self):
        limits = httpx.Limits(
            max_keepalive_connections=50, 
            max_connections=settings.MAX_CONCURRENT_REQUESTS + 20
        )
        timeout = httpx.Timeout(settings.REQUEST_TIMEOUT_SECONDS, connect=5.0)
        proxy_url = settings.PROXY_DSN.strip() if settings.PROXY_DSN and settings.PROXY_DSN.strip() else None
        self.client = httpx.AsyncClient(
            limits=limits,
            timeout=timeout,
            proxy=proxy_url,
            http2=False
        )
        logger.info("Initialized HTTPX Async Client pool.")

    async def stop(self):
        if self.client:
            await self.client.aclose()
            logger.info("Closed HTTPX Async Client pool.")

    def _get_headers(self) -> Dict[str, str]:
        # Strip surrounding double quotes from JSESSIONID to format csrf-token
        clean_csrf = settings.LINKEDIN_JSESSIONID.replace('"', '').strip()
        return {
            "csrf-token": clean_csrf,
            "x-restli-protocol-version": "2.0.0",
            "x-li-lang": "en_US",
            "accept": "application/vnd.linkedin.normalized+json+2.1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

    def _get_cookies(self) -> Dict[str, str]:
        return {
            "li_at": settings.LINKEDIN_LI_AT,
            "JSESSIONID": settings.LINKEDIN_JSESSIONID
        }

    async def fetch_profile(self, target_slug: str) -> ProfileResponse:
        async with self.semaphore:
            url = "https://www.linkedin.com/voyager/api/identity/dash/profiles"
            params = {
                "q": "memberIdentity",
                "memberIdentity": target_slug,
                "decorationId": "com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-93"
            }
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await self.client.get(
                        url,
                        params=params,
                        headers=self._get_headers(),
                        cookies=self._get_cookies()
                    )
                    
                    if response.status_code == 200:
                        return parse_voyager_response(response.json(), target_slug)
                    
                    elif response.status_code == 404:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Profile '{target_slug}' was not found or is private."
                        )
                    elif response.status_code in (401, 403):
                        logger.error(f"Authentication rejected by Voyager API: {response.status_code}")
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="Upstream session credentials invalid or revoked."
                        )
                    elif response.status_code == 429:
                        if attempt == max_retries - 1:
                            raise HTTPException(
                                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                detail="Rate limit exceeded on upstream providers."
                            )
                        # Exponential backoff with jitter computation
                        sleep_time = (2 ** attempt) + random.uniform(0.1, 0.5)
                        logger.warning(f"Rate limited (429). Retrying in {sleep_time:.2f}s...")
                        await asyncio.sleep(sleep_time)
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Upstream provider returned code: {response.status_code}"
                        )

                except httpx.RequestError as exc:
                    if attempt == max_retries - 1:
                        logger.error(f"Network transport error: {str(exc)}")
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Upstream network transport error."
                        )
                    await asyncio.sleep(1.0)

voyager_transport = VoyagerTransportClient()
