from urllib.parse import urlparse
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, Response
import logging
import asyncio

TAG = "Proxy"
PREFIX = "/proxy"

router = APIRouter()

logger = logging.getLogger(__name__)

@router.options("/")
async def proxy_options():
    """Handle CORS preflight requests for the proxy endpoint"""
    return Response(
        status_code=200,
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Max-Age': '86400',
        }
    )

@router.get("/")
async def proxy_request(url: str):
    """
    Proxy endpoint that fetches a resource and returns it with CORS headers.
    Usage: GET /proxy?url=https://example.com/model.glb
    """
    
    parsed_url = urlparse(url)
    allowed_domains = ["tripo-data.rg1.data.tripo3d.com"]
    
    if parsed_url.netloc not in allowed_domains:
        raise HTTPException(status_code=403, detail="Domain not allowed")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            response = await client.get(url, follow_redirects=True)
            
            response.raise_for_status()

            content_type = response.headers.get("content-type", "application/octet-stream")

            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                    "Content-Length": str(len(response.content)),
                    "Cache-Control": "public, max-age=3600",
                }
            )
            
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching URL: {url}")
        raise HTTPException(status_code=408, detail="Request timeout")
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching URL: {url}, Status: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Upstream server error: {e.response.status_code}")
    
    except Exception as e:
        logger.error(f"Error fetching URL: {url}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
