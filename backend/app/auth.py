import os
import sys
import random
import secrets
import hashlib
from datetime import datetime, timedelta
import bcrypt
import resend
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, EmailStr, field_validator
from fastapi import APIRouter, HTTPException, Request
from supabase import create_client, Client

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.rate_limiter import limiter
from utils.audit_logger import AuditLogger

router = APIRouter(prefix="/api/auth", tags=["auth"])

SESSION_EXPIRY_DAYS = 7
VERIFICATION_CODE_EXPIRY_MINUTES = 15

resend.api_key = os.environ.get("RESEND_API_KEY")

def get_base_url() -> str:
    base_url = os.environ.get("APP_BASE_URL")
    if base_url:
        return base_url
    replit_domain = os.environ.get("REPLIT_DOMAINS", "").split(",")[0]
    if replit_domain:
        return f"https://{replit_domain}"
    return ""

def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return create_client(url, key)
    return None

def get_db_connection():
    """Get direct PostgreSQL connection using individual params to handle special chars in password."""
    from urllib.parse import urlparse, unquote
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        parsed = urlparse(database_url)
        return psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=unquote(parsed.username) if parsed.username else None,
            password=unquote(parsed.password) if parsed.password else None,
            database=parsed.path.lstrip('/') if parsed.path else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def save_session_to_db(user_id: str, token_hash: str, expires_at: datetime) -> bool:
    """Save session using direct database connection (more reliable than Supabase client)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO user_sessions (user_id, token_hash, expires_at) 
               VALUES (%s, %s, %s)""",
            (user_id, token_hash, expires_at)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Session save error: {e}")
        return False

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
    email: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserData(BaseModel):
    id: str
    email: str
    name: str | None
    profile_name: str | None
    is_verified: bool = False
    is_admin: bool = False

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

class SendVerificationRequest(BaseModel):
    email: EmailStr

class SendVerificationResponse(BaseModel):
    success: bool
    message: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str

class VerifyEmailResponse(BaseModel):
    success: bool
    message: str

class GoogleAuthRequest(BaseModel):
    access_token: str

class GoogleAuthResponse(BaseModel):
    success: bool
    message: str
    token: str | None = None
    user: dict | None = None

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

def generate_verification_code() -> str:
    return str(random.randint(100000, 999999))

def send_verification_email(email: str, code: str, name: str | None = None, base_url: str | None = None) -> bool:
    try:
        user_name = name or "there"
        import urllib.parse
        encoded_email = urllib.parse.quote(email)
        verify_url = f"{base_url}/verify-email?email={encoded_email}&code={code}" if base_url else f"/verify-email?email={encoded_email}&code={code}"
        
        resend.Emails.send({
            "from": "GetHiredAlly <noreply@gethiredally.com>",
            "to": email,
            "subject": "Verify your GetHiredAlly account",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #1E3A5F; margin: 0;">GetHiredAlly</h1>
                </div>
                <div style="background-color: #FAF9F7; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #333333; margin-top: 0;">Verify your email address</h2>
                    <p style="color: #333333;">Hi {user_name},</p>
                    <p style="color: #333333;">Thanks for signing up for GetHiredAlly! Please use the verification code below to confirm your email address:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="background-color: #1E3A5F; color: white; font-size: 32px; font-weight: bold; letter-spacing: 8px; padding: 20px 40px; border-radius: 8px; display: inline-block;">
                            {code}
                        </div>
                    </div>
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="{verify_url}" style="background-color: #1E3A5F; color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-size: 16px; font-weight: bold; display: inline-block;">Verify Now</a>
                    </div>
                    <p style="color: #666666; font-size: 14px; text-align: center;">This code will expire in 15 minutes.</p>
                    <p style="color: #333333;">If you didn't create an account with GetHiredAlly, you can safely ignore this email.</p>
                </div>
                <div style="text-align: center; margin-top: 20px; color: #999999; font-size: 12px;">
                    <p>GetHiredAlly - Your Interview Success Partner</p>
                </div>
            </div>
            """
        })
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@router.post("/register", response_model=RegisterResponse)
@limiter.limit("10/hour")
async def register_user(request: Request, data: RegisterRequest):
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    try:
        existing = client.table("users").select("id").eq("email", data.email.lower()).execute()
        if existing.data and len(existing.data) > 0:
            raise HTTPException(status_code=400, detail="An account with this email already exists")
        
        profile_result = client.table("user_profiles").select("id").eq("profile_name", "standard").execute()
        if not profile_result.data or len(profile_result.data) == 0:
            raise HTTPException(status_code=500, detail="Default user profile not found. Please run database setup.")
        
        default_profile_id = profile_result.data[0]["id"]
        
        password_hash = hash_password(data.password)
        
        user_data = {
            "email": data.email.lower(),
            "password_hash": password_hash,
            "name": data.name,
            "profile_id": default_profile_id,
            "is_verified": False,
            "is_admin": False
        }
        
        result = client.table("users").insert(user_data).execute()
        
        if result.data and len(result.data) > 0:
            user_id = result.data[0]["id"]
            
            code = generate_verification_code()
            expires_at = datetime.utcnow() + timedelta(minutes=VERIFICATION_CODE_EXPIRY_MINUTES)
            
            client.table("email_verification_codes").insert({
                "user_id": user_id,
                "code": code,
                "expires_at": expires_at.isoformat(),
                "used": False
            }).execute()
            
            send_verification_email(data.email.lower(), code, data.name, get_base_url())
            
            return RegisterResponse(
                success=True,
                message="Registration successful! Please check your email for a verification code.",
                user_id=user_id,
                email=data.email.lower()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create user account")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/send-verification", response_model=SendVerificationResponse)
@limiter.limit("5/hour")
async def send_verification_code(request: Request, data: SendVerificationRequest):
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    try:
        user_result = client.table("users").select("id, name, is_verified").eq("email", data.email.lower()).execute()
        
        if not user_result.data or len(user_result.data) == 0:
            raise HTTPException(status_code=404, detail="No account found with this email")
        
        user = user_result.data[0]
        
        if user.get("is_verified"):
            return SendVerificationResponse(
                success=True,
                message="Email is already verified"
            )
        
        code = generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=VERIFICATION_CODE_EXPIRY_MINUTES)
        
        client.table("email_verification_codes").insert({
            "user_id": user["id"],
            "code": code,
            "expires_at": expires_at.isoformat(),
            "used": False
        }).execute()
        
        email_sent = send_verification_email(data.email.lower(), code, user.get("name"), get_base_url())
        
        if email_sent:
            return SendVerificationResponse(
                success=True,
                message="Verification code sent to your email"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to send verification email")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification: {str(e)}")

@router.post("/verify-email", response_model=VerifyEmailResponse)
@limiter.limit("10/hour")
async def verify_email(request: Request, data: VerifyEmailRequest):
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    try:
        user_result = client.table("users").select("id, is_verified").eq("email", data.email.lower()).execute()
        
        if not user_result.data or len(user_result.data) == 0:
            raise HTTPException(status_code=404, detail="No account found with this email")
        
        user = user_result.data[0]
        
        if user.get("is_verified"):
            return VerifyEmailResponse(
                success=True,
                message="Email is already verified"
            )
        
        code_result = client.table("email_verification_codes").select(
            "id, code, expires_at, used"
        ).eq("user_id", user["id"]).eq("code", data.code).eq("used", False).execute()
        
        if not code_result.data or len(code_result.data) == 0:
            raise HTTPException(status_code=400, detail="Invalid verification code")
        
        code_record = code_result.data[0]
        expires_at = datetime.fromisoformat(code_record["expires_at"].replace("Z", "+00:00"))
        
        if expires_at < datetime.utcnow().replace(tzinfo=expires_at.tzinfo):
            raise HTTPException(status_code=400, detail="Verification code has expired. Please request a new one.")
        
        client.table("users").update({"is_verified": True}).eq("id", user["id"]).execute()
        
        client.table("email_verification_codes").update({"used": True}).eq("id", code_record["id"]).execute()
        
        return VerifyEmailResponse(
            success=True,
            message="Email verified successfully! You can now log in."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login_user(request: Request, data: LoginRequest):
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    ip_address = request.client.host if request.client else "unknown"
    
    try:
        user_result = client.table("users").select(
            "id, email, name, password_hash, profile_id, is_verified, is_admin"
        ).eq("email", data.email.lower()).execute()
        
        if not user_result.data or len(user_result.data) == 0:
            AuditLogger.log_login_attempt(
                email=data.email,
                success=False,
                ip_address=ip_address,
                reason="User not found"
            )
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user = user_result.data[0]
        
        if not verify_password(data.password, user["password_hash"]):
            AuditLogger.log_login_attempt(
                email=data.email,
                success=False,
                ip_address=ip_address,
                reason="Invalid password"
            )
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        profile_name = None
        if user.get("profile_id"):
            profile_result = client.table("user_profiles").select("profile_name").eq("id", user["profile_id"]).execute()
            if profile_result.data and len(profile_result.data) > 0:
                profile_name = profile_result.data[0]["profile_name"]
        
        session_token = generate_session_token()
        token_hash = hash_token(session_token)
        expires_at = datetime.utcnow() + timedelta(days=SESSION_EXPIRY_DAYS)
        
        if not save_session_to_db(user["id"], token_hash, expires_at):
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        client.table("users").update({"last_login": datetime.utcnow().isoformat()}).eq("id", user["id"]).execute()
        
        AuditLogger.log_login_attempt(
            email=data.email,
            success=True,
            ip_address=ip_address
        )
        
        return LoginResponse(
            success=True,
            message="Login successful!",
            token=session_token,
            user=UserData(
                id=user["id"],
                email=user["email"],
                name=user.get("name"),
                profile_name=profile_name,
                is_verified=user.get("is_verified", False),
                is_admin=user.get("is_admin", False)
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/google", response_model=GoogleAuthResponse)
async def google_auth(request: Request, data: GoogleAuthRequest):
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    ip_address = request.client.host if request.client else "unknown"
    
    try:
        async with httpx.AsyncClient() as http_client:
            google_response = await http_client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {data.access_token}'}
            )
        
        if google_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        
        google_user = google_response.json()
        google_id = google_user.get('id')
        email = google_user.get('email')
        name = google_user.get('name')
        picture = google_user.get('picture')
        
        if not email or not google_id:
            raise HTTPException(status_code=400, detail="Could not get user info from Google")
        
        user = None
        user_result = client.table("users").select("*").eq("google_id", google_id).execute()
        
        if user_result.data and len(user_result.data) > 0:
            user = user_result.data[0]
        else:
            email_result = client.table("users").select("*").eq("email", email.lower()).execute()
            
            if email_result.data and len(email_result.data) > 0:
                user = email_result.data[0]
                update_data = {
                    "google_id": google_id,
                    "is_verified": True
                }
                if picture and not user.get("profile_picture_url"):
                    update_data["profile_picture_url"] = picture
                if not user.get("auth_provider"):
                    update_data["auth_provider"] = "google"
                
                client.table("users").update(update_data).eq("id", user["id"]).execute()
                user.update(update_data)
            else:
                profile_result = client.table("user_profiles").select("id").eq("profile_name", "standard").execute()
                if not profile_result.data or len(profile_result.data) == 0:
                    raise HTTPException(status_code=500, detail="Default user profile not found")
                
                default_profile_id = profile_result.data[0]["id"]
                
                new_user_data = {
                    "email": email.lower(),
                    "name": name,
                    "google_id": google_id,
                    "auth_provider": "google",
                    "profile_picture_url": picture,
                    "is_verified": True,
                    "is_admin": False,
                    "profile_id": default_profile_id
                }
                
                result = client.table("users").insert(new_user_data).execute()
                if result.data and len(result.data) > 0:
                    user = result.data[0]
                else:
                    raise HTTPException(status_code=500, detail="Failed to create user account")
        
        session_token = generate_session_token()
        token_hash = hash_token(session_token)
        expires_at = datetime.utcnow() + timedelta(days=SESSION_EXPIRY_DAYS)
        
        if not save_session_to_db(user["id"], token_hash, expires_at):
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        client.table("users").update({"last_login": datetime.utcnow().isoformat()}).eq("id", user["id"]).execute()
        
        profile_name = None
        if user.get("profile_id"):
            profile_result = client.table("user_profiles").select("profile_name").eq("id", user["profile_id"]).execute()
            if profile_result.data and len(profile_result.data) > 0:
                profile_name = profile_result.data[0]["profile_name"]
        
        AuditLogger.log_login_attempt(
            email=email,
            success=True,
            ip_address=ip_address
        )
        
        return GoogleAuthResponse(
            success=True,
            message="Google sign-in successful!",
            token=session_token,
            user={
                "id": user["id"],
                "email": user["email"],
                "name": user.get("name"),
                "profile_name": profile_name,
                "profile_picture_url": user.get("profile_picture_url"),
                "is_verified": True,
                "is_admin": user.get("is_admin", False)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        AuditLogger.log_login_attempt(
            email="google_auth",
            success=False,
            ip_address=ip_address,
            reason=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Google authentication failed: {str(e)}")

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
        
        user_result = client.table("users").select("id, email, name, profile_id, is_verified, is_admin").eq("id", session["user_id"]).execute()
        
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
            "profile_name": profile_name,
            "is_verified": user.get("is_verified", False),
            "is_admin": user.get("is_admin", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")
