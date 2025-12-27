"""Pydantic input validation models for all API endpoints."""
import re
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator


def sanitize_text(value: str) -> str:
    """Remove HTML tags and dangerous characters from text input."""
    if not value:
        return value
    cleaned = re.sub(r'<[^>]*>', '', value)
    cleaned = re.sub(r'[<>]', '', cleaned)
    return cleaned.strip()


def validate_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError):
        return False


class UserRegisterInput(BaseModel):
    """Validated input for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        sanitized = sanitize_text(v)
        if not sanitized:
            raise ValueError('Name is required')
        return sanitized
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserLoginInput(BaseModel):
    """Validated input for user login."""
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class TokenInput(BaseModel):
    """Validated input for token-based requests."""
    token: str = Field(..., min_length=1, max_length=256)


class SendVerificationInput(BaseModel):
    """Validated input for sending verification email."""
    email: EmailStr


class VerifyEmailInput(BaseModel):
    """Validated input for email verification."""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')


class JobDescriptionInput(BaseModel):
    """Validated input for job description analysis."""
    job_description: str = Field(..., min_length=10, max_length=50000)
    mode: str = Field(default='standard')
    interviewer_type: str = Field(default='general')
    provider: str = Field(default='claude')
    
    @field_validator('job_description')
    @classmethod
    def sanitize_job_description(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError('Job description must be at least 10 characters')
        return v.strip()
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v: str) -> str:
        allowed = ['quick', 'standard', 'deep', 'max']
        if v.lower() not in allowed:
            raise ValueError(f'Mode must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @field_validator('interviewer_type')
    @classmethod
    def validate_interviewer_type(cls, v: str) -> str:
        allowed = ['hr', 'technical', 'manager', 'general']
        if v.lower() not in allowed:
            raise ValueError(f'Interviewer type must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        allowed = ['claude', 'gemini']
        if v.lower() not in allowed:
            raise ValueError(f'Provider must be one of: {", ".join(allowed)}')
        return v.lower()


class CVInput(BaseModel):
    """Validated input for CV/resume content."""
    content: str = Field(..., min_length=10, max_length=100000)
    
    @field_validator('content')
    @classmethod
    def validate_cv_content(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError('CV content must be at least 10 characters')
        return v.strip()


class SmartQuestionsInput(BaseModel):
    """Validated input for smart questions generation."""
    xray_analysis_id: Optional[str] = None
    job_description: Optional[str] = Field(None, max_length=50000)
    cv_text: Optional[str] = Field(None, max_length=100000)
    token: str = Field(..., min_length=1, max_length=256)
    provider: str = Field(default='gemini')
    
    @field_validator('xray_analysis_id')
    @classmethod
    def validate_xray_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            if not validate_uuid(v):
                raise ValueError('Invalid analysis ID format')
        return v
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        allowed = ['claude', 'gemini']
        if v.lower() not in allowed:
            raise ValueError(f'Provider must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @field_validator('job_description')
    @classmethod
    def validate_job_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip() if v.strip() else None
        return v
    
    @field_validator('cv_text')
    @classmethod
    def validate_cv_text(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class XRayInput(BaseModel):
    """Validated input for X-Ray analysis."""
    job_description: str = Field(..., min_length=10, max_length=50000)
    mode: str = Field(default='standard')
    interviewer_type: str = Field(default='general')
    provider: str = Field(default='claude')
    token: Optional[str] = Field(None, max_length=256)
    
    @field_validator('job_description')
    @classmethod
    def validate_job_description(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError('Job description must be at least 10 characters')
        return v.strip()
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v: str) -> str:
        allowed = ['quick', 'standard', 'deep', 'max']
        if v.lower() not in allowed:
            raise ValueError(f'Mode must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @field_validator('interviewer_type')
    @classmethod
    def validate_interviewer_type(cls, v: str) -> str:
        allowed = ['hr', 'technical', 'manager', 'general']
        if v.lower() not in allowed:
            raise ValueError(f'Interviewer type must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        allowed = ['claude', 'gemini']
        if v.lower() not in allowed:
            raise ValueError(f'Provider must be one of: {", ".join(allowed)}')
        return v.lower()


class FileUploadValidation:
    """File upload validation utilities."""
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    
    @classmethod
    def validate_extension(cls, filename: str) -> str:
        """Validate file extension and return the extension."""
        if not filename or '.' not in filename:
            raise ValueError('Invalid filename')
        
        extension = filename.rsplit('.', 1)[-1].lower()
        if extension not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f'Invalid file type. Allowed: {", ".join(cls.ALLOWED_EXTENSIONS)}')
        
        return extension
    
    @classmethod
    def validate_size(cls, content_length: int) -> None:
        """Validate file size."""
        if content_length > cls.MAX_FILE_SIZE:
            max_mb = cls.MAX_FILE_SIZE // (1024 * 1024)
            raise ValueError(f'File too large. Maximum size: {max_mb}MB')
