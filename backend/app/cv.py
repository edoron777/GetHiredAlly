"""CV upload and management endpoints."""
import os
import sys
import io
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from supabase import create_client, Client

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.encryption import encrypt_text
from config.rate_limiter import limiter

router = APIRouter(prefix="/api/cv", tags=["cv"])

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = ['pdf', 'docx', 'doc', 'txt']

def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def get_user_from_token(token: str) -> dict | None:
    """Get user from session token."""
    import hashlib
    client = get_supabase_client()
    if not client or not token:
        return None
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    session_result = client.table("user_sessions").select("user_id, expires_at").eq("token_hash", token_hash).execute()
    
    if not session_result.data:
        return None
    
    session = session_result.data[0]
    user_result = client.table("users").select("*").eq("id", session["user_id"]).execute()
    
    if not user_result.data:
        return None
    
    return user_result.data[0]


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text content from uploaded file."""
    extension = filename.split('.')[-1].lower()
    
    if extension == 'txt':
        return file_content.decode('utf-8', errors='ignore')
    
    elif extension == 'pdf':
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                return '\n'.join(text_parts)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")
    
    elif extension in ['docx', 'doc']:
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_content))
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            return '\n'.join(text_parts)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse DOCX: {str(e)}")
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")


@router.get("/list")
async def list_user_cvs(token: str):
    """List all CVs for authenticated user."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        result = client.table("user_cvs").select(
            "id, filename, created_at"
        ).eq("user_id", user["id"]).order("created_at", desc=True).execute()
        
        return {"cvs": result.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-for-scan")
async def upload_cv_for_scan(
    file: UploadFile = File(...),
    token: str = Form(...)
):
    """Upload a CV file, extract text, and save to database."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    extension = file.filename.split('.')[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: PDF, DOCX, TXT")
    
    file_content = await file.read()
    
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum 10MB allowed")
    
    text_content = extract_text_from_file(file_content, file.filename)
    
    if not text_content or len(text_content.strip()) < 50:
        raise HTTPException(status_code=400, detail="Could not extract sufficient text from file")
    
    encrypted_content = encrypt_text(text_content)
    
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        cv_data = {
            "user_id": str(user["id"]),
            "filename": file.filename,
            "original_filename": file.filename,
            "content": encrypted_content,
            "file_size": len(file_content),
            "file_type": extension
        }
        
        result = client.table("user_cvs").insert(cv_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save CV")
        
        cv_id = result.data[0]["id"]
        
        return {
            "cv_id": cv_id,
            "filename": file.filename,
            "size": len(file_content),
            "content_length": len(text_content)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save CV: {str(e)}")


@router.get("/{cv_id}")
async def get_cv(cv_id: str, token: str):
    """Get a specific CV's content."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        result = client.table("user_cvs").select("*").eq("id", cv_id).eq("user_id", user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="CV not found")
        
        cv = result.data[0]
        
        return {
            "id": cv["id"],
            "filename": cv["filename"],
            "file_type": cv["file_type"],
            "file_size": cv["file_size"],
            "created_at": cv["created_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
