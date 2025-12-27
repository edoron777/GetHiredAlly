"""Rate limiting configuration for API endpoints."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse


limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors with user-friendly message."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests. Please try again later.",
            "detail": str(exc.detail) if exc.detail else "Rate limit exceeded"
        }
    )
