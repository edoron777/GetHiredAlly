import os
import bcrypt
from pydantic import BaseModel, EmailStr, field_validator
from fastapi import APIRouter, HTTPException
from supabase import create_client, Client

router = APIRouter(prefix="/api/auth", tags=["auth"])

def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if url and key:
        return create_client(url, key)
    return None

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name is required')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: str | None = None

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

@router.post("/register", response_model=RegisterResponse)
async def register_user(request: RegisterRequest):
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    try:
        existing = client.table("users").select("id").eq("email", request.email.lower()).execute()
        if existing.data and len(existing.data) > 0:
            raise HTTPException(status_code=400, detail="An account with this email already exists")
        
        profile_result = client.table("user_profiles").select("id").eq("profile_name", "standard").execute()
        if not profile_result.data or len(profile_result.data) == 0:
            raise HTTPException(status_code=500, detail="Default user profile not found. Please run database setup.")
        
        default_profile_id = profile_result.data[0]["id"]
        
        password_hash = hash_password(request.password)
        
        user_data = {
            "email": request.email.lower(),
            "password_hash": password_hash,
            "name": request.name,
            "profile_id": default_profile_id,
            "is_verified": False,
            "is_admin": False
        }
        
        result = client.table("users").insert(user_data).execute()
        
        if result.data and len(result.data) > 0:
            return RegisterResponse(
                success=True,
                message="Registration successful! You can now log in.",
                user_id=result.data[0]["id"]
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create user account")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
