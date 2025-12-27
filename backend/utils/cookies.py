"""Secure cookie utilities."""
import os
from fastapi import Response


def is_production() -> bool:
    """Check if running in production (HTTPS required)."""
    return os.environ.get("REPLIT_DEPLOYMENT") == "1"


def set_secure_cookie(
    response: Response,
    key: str,
    value: str,
    max_age: int = 604800
):
    """
    Set a cookie with security flags enabled.
    
    Args:
        response: FastAPI response object
        key: Cookie name
        value: Cookie value
        max_age: Expiration in seconds (default 7 days = 604800)
    """
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=is_production(),
        samesite="lax",
        max_age=max_age,
        path="/"
    )


def delete_secure_cookie(response: Response, key: str):
    """Delete a cookie securely."""
    response.delete_cookie(
        key=key,
        httponly=True,
        secure=is_production(),
        samesite="lax",
        path="/"
    )
