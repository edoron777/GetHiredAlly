"""Rate limiting configuration for API endpoints."""
import sys
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.audit_logger import AuditLogger

limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors with user-friendly message."""
    ip_address = request.client.host if request.client else "unknown"
    
    AuditLogger.log_security_event(
        event_type="RATE_LIMIT_EXCEEDED",
        details=f"Endpoint: {request.url.path}",
        ip_address=ip_address
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests. Please try again later.",
            "detail": str(exc.detail) if exc.detail else "Rate limit exceeded"
        }
    )
