import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, Response
import logging
import asyncio

TAG = "Proxy"
PREFIX = "/proxy"

router = APIRouter()

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
async def proxy(url: str):
    """
    Proxies a GET request to the given URL and streams the response.
    This is used to bypass CORS issues for resources like 3D models.
    """
    # Configure httpx client with longer timeouts for large files
    timeout = httpx.Timeout(120.0, connect=60.0)  # 2 minutes total, 1 minute for connection
    
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        try:
            logging.info(f"Proxying request to: {url}")
            print(f"Proxying request to: {url}")
            
            # Make a streaming request to avoid loading large files into memory
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                
                # Get content type and other headers
                content_type = response.headers.get('content-type', 'application/octet-stream')
                content_length = response.headers.get('content-length')
                
                logging.info(f"Proxying file with content-type: {content_type}, size: {content_length}")
                print(f"Proxying file with content-type: {content_type}, size: {content_length}")
                
                # Create a streaming response that yields chunks
                async def stream_content():
                    chunk_count = 0
                    total_bytes = 0
                    try:
                        async for chunk in response.aiter_bytes():
                            chunk_count += 1
                            total_bytes += len(chunk)
                            if chunk_count % 100 == 0:  # Log every 100 chunks
                                print(f"Streamed {chunk_count} chunks, {total_bytes} bytes")
                            yield chunk
                        print(f"Completed streaming: {chunk_count} chunks, {total_bytes} bytes")
                    except httpx.StreamClosed:
                        print(f"Client disconnected during streaming after {chunk_count} chunks, {total_bytes} bytes")
                        # Client disconnected, this is normal - don't raise an exception
                        # Just return without yielding anything more
                        return
                    except asyncio.TimeoutError:
                        print(f"Streaming timeout after {chunk_count} chunks, {total_bytes} bytes")
                        return
                    except Exception as e:
                        print(f"Error during streaming: {e}")
                        # Only raise if it's not a client disconnection
                        if not isinstance(e, (httpx.StreamClosed, asyncio.TimeoutError)):
                            raise
                        # For client disconnections, just return gracefully
                        return
                
                headers = {
                    'Content-Type': content_type,
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': '*',
                }
                
                # Add content length if available
                if content_length:
                    headers['Content-Length'] = content_length
                
                try:
                    return StreamingResponse(
                        stream_content(),
                        headers=headers,
                        media_type=content_type
                    )
                except httpx.StreamClosed:
                    print(f"Stream closed during response creation for {url}")
                    return Response(
                        status_code=499,
                        content="Client closed request",
                        headers={'Access-Control-Allow-Origin': '*'}
                    )
                except Exception as e:
                    print(f"Error creating streaming response for {url}: {e}")
                    # If it's a StreamClosed or similar client disconnection, return 499
                    if "StreamClosed" in str(e) or "stream" in str(e).lower():
                        return Response(
                            status_code=499,
                            content="Client closed request",
                            headers={'Access-Control-Allow-Origin': '*'}
                        )
                    # Otherwise, re-raise as a proper HTTP exception
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error creating streaming response: {str(e)}"
                    )
                
        except httpx.RequestError as exc:
            logging.error(f"Request error while proxying {url}: {exc}")
            print(f"Request error while proxying {url}: {exc}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch resource: {str(exc)}"
            )
        except httpx.HTTPStatusError as exc:
            logging.error(f"HTTP error while proxying {url}: {exc.response.status_code}")
            print(f"HTTP error while proxying {url}: {exc.response.status_code}")
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Resource returned error {exc.response.status_code}"
            )
        except httpx.StreamClosed as exc:
            logging.info(f"Client disconnected during streaming of {url}: {exc}")
            print(f"Client disconnected during streaming of {url}: {exc}")
            # Client disconnected - this is normal, return a 499 status (Client Closed Request)
            return Response(
                status_code=499,
                content="Client closed request",
                headers={'Access-Control-Allow-Origin': '*'}
            )
        except Exception as exc:
            # Check if this is a StreamClosed exception that wasn't caught earlier
            if "StreamClosed" in str(exc) or "stream" in str(exc).lower():
                logging.info(f"Client disconnected during streaming of {url} (caught in general exception): {exc}")
                print(f"Client disconnected during streaming of {url} (caught in general exception): {exc}")
                return Response(
                    status_code=499,
                    content="Client closed request",
                    headers={'Access-Control-Allow-Origin': '*'}
                )
            
            logging.error(f"Unexpected error while proxying {url}: {exc}")
            print(f"Unexpected error while proxying {url}: {exc}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(exc)}"
            ) 