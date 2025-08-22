from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.utils import RateLimiter, log_api_request
from app.monitoring import metrics
import time
import logging

logger = logging.getLogger(__name__)
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

async def log_requests(request: Request, call_next):
    """
    Middleware to log all requests
    """
    start_time = time.time()
    
    log_api_request(
        endpoint=str(request.url.path),
        method=request.method,
        client_id=request.client.host
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Record metrics
        metrics.record_request(str(request.url.path), process_time)
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        metrics.record_error()
        raise e

async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware for rate limiting
    """
    client_id = request.client.host
    
    if not rate_limiter.is_allowed(client_id):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )
    
    response = await call_next(request)
    return response

async def error_handler(request: Request, exc: Exception):
    """
    Global error handler
    """
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if request.app.debug else "An error occurred"
        }
    )