import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

TAG = "Proxy"
PREFIX = "/proxy"

router = APIRouter()

@router.get("/")
async def proxy(url: str):
    """
    Proxies a GET request to the given URL and streams the response.
    This is used to bypass CORS issues for resources like 3D models.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Stream the request to the target URL to handle potentially large files
            req = await client.get(url, follow_redirects=True)
            req.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            content_type = req.headers.get('content-type', 'application/octet-stream')

            return StreamingResponse(req.iter_bytes(), headers={'Content-Type': content_type})

        except httpx.RequestError as exc:
            return {"detail": f"An error occurred while requesting {exc.request.url!r}: {exc}"}, 500
        except httpx.HTTPStatusError as exc:
            return {"detail": f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."}, exc.response.status_code 