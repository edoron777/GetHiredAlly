"""Security headers middleware for protection against common web attacks."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=()"
        )
        
        return response
