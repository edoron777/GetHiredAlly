import os
import secrets
import hashlib
from datetime import datetime, timedelta
import bcrypt
from pydantic import BaseModel, EmailStr, field_validator
from fastapi import APIRouter, HTTPException
from supabase import create_client, Client

router = APIRouter(prefix="/api/auth", tags=["auth"])

SESSION_EXPIRY_DAYS = 7

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

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserData(BaseModel):
    id: str
    email: str
    name: str | None
    profile_name: str | None

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: str | None = None
    user: UserData | None = None

class LogoutRequest(BaseModel):
    token: str

class LogoutResponse(BaseModel):
    success: bool
    message: str

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

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

@router.post("/login", response_model=LoginResponse)
async def login_user(request: LoginRequest):
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    try:
        user_result = client.table("users").select(
            "id, email, name, password_hash, profile_id"
        ).eq("email", request.email.lower()).execute()
        
        if not user_result.data or len(user_result.data) == 0:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user = user_result.data[0]
        
        if not verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        profile_name = None
        if user.get("profile_id"):
            profile_result = client.table("user_profiles").select("profile_name").eq("id", user["profile_id"]).execute()
            if profile_result.data and len(profile_result.data) > 0:
                profile_name = profile_result.data[0]["profile_name"]
        
        session_token = generate_session_token()
        token_hash = hash_token(session_token)
        expires_at = datetime.utcnow() + timedelta(days=SESSION_EXPIRY_DAYS)
        
        session_data = {
            "user_id": user["id"],
            "token_hash": token_hash,
            "expires_at": expires_at.isoformat()
        }
        client.table("user_sessions").insert(session_data).execute()
        
        client.table("users").update({"last_login": datetime.utcnow().isoformat()}).eq("id", user["id"]).execute()
        
        return LoginResponse(
            success=True,
            message="Login successful!",
            token=session_token,
            user=UserData(
                id=user["id"],
                email=user["email"],
                name=user.get("name"),
                profile_name=profile_name
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/logout", response_model=LogoutResponse)
async def logout_user(request: LogoutRequest):
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    try:
        token_hash = hash_token(request.token)
        client.table("user_sessions").delete().eq("token_hash", token_hash).execute()
        
        return LogoutResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@router.get("/me")
async def get_current_user(token: str):
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    try:
        token_hash = hash_token(token)
        session_result = client.table("user_sessions").select("user_id, expires_at").eq("token_hash", token_hash).execute()
        
        if not session_result.data or len(session_result.data) == 0:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        session = session_result.data[0]
        expires_at = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
        
        if expires_at < datetime.utcnow().replace(tzinfo=expires_at.tzinfo):
            client.table("user_sessions").delete().eq("token_hash", token_hash).execute()
            raise HTTPException(status_code=401, detail="Session expired")
        
        user_result = client.table("users").select("id, email, name, profile_id").eq("id", session["user_id"]).execute()
        
        if not user_result.data or len(user_result.data) == 0:
            raise HTTPException(status_code=401, detail="User not found")
        
        user = user_result.data[0]
        
        profile_name = None
        if user.get("profile_id"):
            profile_result = client.table("user_profiles").select("profile_name").eq("id", user["profile_id"]).execute()
            if profile_result.data and len(profile_result.data) > 0:
                profile_name = profile_result.data[0]["profile_name"]
        
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user.get("name"),
            "profile_name": profile_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")
