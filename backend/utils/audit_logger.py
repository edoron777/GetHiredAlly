"""Secure audit logger - NEVER logs sensitive data like passwords or tokens."""
import logging
import json
import os
from datetime import datetime
from typing import Optional

log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)

if not audit_logger.handlers:
    file_handler = logging.FileHandler(os.path.join(log_dir, 'audit.log'))
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    audit_logger.addHandler(file_handler)


class AuditLogger:
    """Secure audit logger - NEVER logs sensitive data."""
    
    @staticmethod
    def _get_safe_ip(request) -> str:
        """Extract IP address safely from request."""
        if request and hasattr(request, 'client') and request.client:
            return request.client.host or "unknown"
        return "unknown"
    
    @staticmethod
    def log_login_attempt(
        email: str,
        success: bool,
        ip_address: str,
        reason: Optional[str] = None
    ):
        """Log login attempt - NEVER log password."""
        event = {
            "event": "LOGIN_ATTEMPT",
            "email": email,
            "success": success,
            "ip": ip_address,
            "reason": reason if not success else None
        }
        level = logging.INFO if success else logging.WARNING
        audit_logger.log(level, json.dumps(event))
    
    @staticmethod
    def log_logout(user_id: str, email: str, ip_address: str):
        """Log user logout."""
        event = {
            "event": "LOGOUT",
            "user_id": user_id,
            "email": email,
            "ip": ip_address
        }
        audit_logger.info(json.dumps(event))
    
    @staticmethod
    def log_registration(
        email: str,
        success: bool,
        ip_address: str,
        user_id: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """Log registration attempt."""
        event = {
            "event": "REGISTRATION",
            "email": email,
            "success": success,
            "user_id": user_id if success else None,
            "ip": ip_address,
            "reason": reason if not success else None
        }
        level = logging.INFO if success else logging.WARNING
        audit_logger.log(level, json.dumps(event))
    
    @staticmethod
    def log_password_change(user_id: str, email: str, ip_address: str):
        """Log password change - NEVER log old or new password."""
        event = {
            "event": "PASSWORD_CHANGE",
            "user_id": user_id,
            "email": email,
            "ip": ip_address
        }
        audit_logger.info(json.dumps(event))
    
    @staticmethod
    def log_data_access(
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        ip_address: str
    ):
        """Log data access (CV view, report generation, etc.)."""
        event = {
            "event": "DATA_ACCESS",
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "ip": ip_address
        }
        audit_logger.info(json.dumps(event))
    
    @staticmethod
    def log_ai_usage(
        user_id: str,
        service: str,
        provider: str,
        ip_address: str
    ):
        """Log AI service usage."""
        event = {
            "event": "AI_USAGE",
            "user_id": user_id,
            "service": service,
            "provider": provider,
            "ip": ip_address
        }
        audit_logger.info(json.dumps(event))
    
    @staticmethod
    def log_admin_action(
        admin_id: str,
        admin_email: str,
        action: str,
        target_user_id: Optional[str],
        details: str,
        ip_address: str
    ):
        """Log admin actions."""
        event = {
            "event": "ADMIN_ACTION",
            "admin_id": admin_id,
            "admin_email": admin_email,
            "action": action,
            "target_user_id": target_user_id,
            "details": details,
            "ip": ip_address
        }
        audit_logger.warning(json.dumps(event))
    
    @staticmethod
    def log_security_event(
        event_type: str,
        details: str,
        ip_address: str,
        user_id: Optional[str] = None
    ):
        """Log security events (rate limit hit, suspicious activity, etc.)."""
        event = {
            "event": "SECURITY_EVENT",
            "type": event_type,
            "details": details,
            "user_id": user_id,
            "ip": ip_address
        }
        audit_logger.warning(json.dumps(event))
