import os
import bcrypt
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException, Header
from supabase import create_client, Client
from typing import Optional
import hashlib

router = APIRouter(prefix="/api/user", tags=["user"])

def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if url and key:
        return create_client(url, key)
    return None

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

async def get_user_from_token(authorization: str) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    token_hash = hash_token(token)
    session_result = client.table("user_sessions").select("user_id").eq("token_hash", token_hash).execute()
    
    if not session_result.data or len(session_result.data) == 0:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    user_id = session_result.data[0]["user_id"]
    user_result = client.table("users").select("*").eq("id", user_id).execute()
    
    if not user_result.data or len(user_result.data) == 0:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user_result.data[0]

class UpdateNameRequest(BaseModel):
    name: str

class UpdateEmailRequest(BaseModel):
    email: EmailStr

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class DeleteAccountRequest(BaseModel):
    password: str

@router.get("/profile")
async def get_profile(authorization: Optional[str] = Header(None)):
    user = await get_user_from_token(authorization)
    
    client = get_supabase_client()
    profile_name = None
    if user.get("profile_id") and client:
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

@router.put("/update-name")
async def update_name(request: UpdateNameRequest, authorization: Optional[str] = Header(None)):
    user = await get_user_from_token(authorization)
    
    if not request.name or not request.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    try:
        client.table("users").update({"name": request.name.strip()}).eq("id", user["id"]).execute()
        return {"success": True, "message": "Name updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update name: {str(e)}")

@router.put("/update-email")
async def update_email(request: UpdateEmailRequest, authorization: Optional[str] = Header(None)):
    user = await get_user_from_token(authorization)
    
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    existing = client.table("users").select("id").eq("email", request.email.lower()).execute()
    if existing.data and len(existing.data) > 0 and existing.data[0]["id"] != user["id"]:
        raise HTTPException(status_code=400, detail="This email is already in use by another account")
    
    try:
        client.table("users").update({
            "email": request.email.lower(),
            "is_verified": False
        }).eq("id", user["id"]).execute()
        return {"success": True, "message": "Email updated successfully. Please verify your new email."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update email: {str(e)}")

@router.put("/change-password")
async def change_password(request: ChangePasswordRequest, authorization: Optional[str] = Header(None)):
    user = await get_user_from_token(authorization)
    
    if not verify_password(request.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    try:
        new_hash = hash_password(request.new_password)
        client.table("users").update({"password_hash": new_hash}).eq("id", user["id"]).execute()
        return {"success": True, "message": "Password changed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")

@router.delete("/delete-account")
async def delete_account(request: DeleteAccountRequest, authorization: Optional[str] = Header(None)):
    user = await get_user_from_token(authorization)
    
    if user.get("is_protected"):
        raise HTTPException(status_code=403, detail="This account cannot be deleted")
    
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Password is incorrect")
    
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    try:
        client.table("user_sessions").delete().eq("user_id", user["id"]).execute()
        client.table("email_verification_codes").delete().eq("user_id", user["id"]).execute()
        client.table("ai_usage_logs").delete().eq("user_id", user["id"]).execute()
        client.table("cv_scans").delete().eq("user_id", user["id"]).execute()
        client.table("smart_questions").delete().eq("user_id", user["id"]).execute()
        client.table("users").delete().eq("id", user["id"]).execute()
        
        return {"success": True, "message": "Account deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete account: {str(e)}")
