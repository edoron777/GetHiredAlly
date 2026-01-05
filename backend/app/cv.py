"""CV upload and management endpoints."""
import os
import sys
import io
import logging
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse, unquote
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from supabase import create_client, Client

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.encryption import encrypt_text
from config.rate_limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cv", tags=["cv"])

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = ['pdf', 'docx', 'doc', 'txt', 'md', 'rtf', 'odt']


def get_db_connection():
    """Get direct PostgreSQL connection using individual params to handle special chars in password."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return None
    
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
        logger.error(f"Failed to parse DATABASE_URL: {e}")
        return None


def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        logger.error(f"Supabase config missing: URL={bool(url)}, KEY={bool(key)}")
        return None
    return create_client(url, key)


def get_user_from_token(token: str) -> dict | None:
    """Get user from session token using direct database connection."""
    if not token:
        return None
    
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        cursor.execute(
            """SELECT s.user_id, s.expires_at, u.id, u.email, u.name, u.profile_id, u.is_verified, u.is_admin
               FROM user_sessions s
               JOIN users u ON s.user_id = u.id
               WHERE s.token_hash = %s""",
            (token_hash,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            return None
        
        return dict(result)
        
    except Exception as e:
        logger.error(f"Database error in get_user_from_token: {str(e)}")
        return None


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
            from docx.opc.constants import RELATIONSHIP_TYPE as RT
            doc = Document(io.BytesIO(file_content))
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            
            relevant_domains = ['linkedin.com', 'github.com', 'gitlab.com', 'bitbucket.org', 'portfolio', 'behance.net', 'dribbble.com']
            hyperlinks = set()
            for rel in doc.part.rels.values():
                if rel.reltype == RT.HYPERLINK and rel.target_ref:
                    link = str(rel.target_ref).lower()
                    if any(domain in link for domain in relevant_domains):
                        hyperlinks.add(rel.target_ref)
            
            text = '\n'.join(text_parts)
            
            if hyperlinks:
                text += "\n\n[HYPERLINKS FOUND IN DOCUMENT:]\n"
                for link in sorted(hyperlinks):
                    text += f"- {link}\n"
            
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse DOCX: {str(e)}")
    
    elif extension == 'md':
        return file_content.decode('utf-8', errors='ignore')
    
    elif extension == 'rtf':
        try:
            from striprtf.striprtf import rtf_to_text
            rtf_content = file_content.decode('utf-8', errors='ignore')
            return rtf_to_text(rtf_content)
        except ImportError:
            text = file_content.decode('utf-8', errors='ignore')
            import re
            text = re.sub(r'\\[a-z]+\d*\s?', '', text)
            text = re.sub(r'[{}]', '', text)
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse RTF: {str(e)}")
    
    elif extension == 'odt':
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            
            with zipfile.ZipFile(io.BytesIO(file_content)) as odt:
                content = odt.read('content.xml')
                root = ET.fromstring(content)
                
                text_parts = []
                for elem in root.iter():
                    if elem.text:
                        text_parts.append(elem.text)
                    if elem.tail:
                        text_parts.append(elem.tail)
                
                return ' '.join(text_parts)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse ODT: {str(e)}")
    
    else:
        try:
            return file_content.decode('utf-8', errors='ignore')
        except Exception:
            raise HTTPException(status_code=400, detail="Unsupported file type")


@router.get("/list")
async def list_user_cvs(token: str):
    """List all CVs for authenticated user."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT id, filename, created_at FROM user_cvs 
               WHERE user_id = %s ORDER BY created_at DESC""",
            (str(user["id"]),)
        )
        cvs = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        return {"cvs": cvs}
    except HTTPException:
        raise
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
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: PDF, DOCX, DOC, TXT, MD, RTF, ODT")
    
    file_content = await file.read()
    
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum 10MB allowed")
    
    text_content = extract_text_from_file(file_content, file.filename)
    
    if not text_content or len(text_content.strip()) < 50:
        raise HTTPException(status_code=400, detail="Could not extract sufficient text from file")
    
    encrypted_content = encrypt_text(text_content)
    
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """INSERT INTO user_cvs (user_id, filename, original_filename, content, file_size, file_type)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (str(user["id"]), file.filename, file.filename, encrypted_content, len(file_content), extension)
        )
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to save CV")
        
        cv_id = result["id"]
        
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
    
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT id, filename, file_type, file_size, created_at FROM user_cvs 
               WHERE id = %s AND user_id = %s""",
            (cv_id, str(user["id"]))
        )
        cv = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")
        
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


@router.get("/dev/test-files")
async def list_test_cv_files():
    """DEV ONLY: List available test CV files."""
    test_cv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_cvs")
    
    if not os.path.exists(test_cv_dir):
        return {"files": []}
    
    files = []
    for filename in os.listdir(test_cv_dir):
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        if ext in ALLOWED_EXTENSIONS:
            filepath = os.path.join(test_cv_dir, filename)
            files.append({
                "name": filename,
                "size": os.path.getsize(filepath)
            })
    
    return {"files": sorted(files, key=lambda x: x["name"])}


from fastapi.responses import FileResponse

@router.get("/dev/test-files/{filename}")
async def get_test_cv_file(filename: str):
    """DEV ONLY: Get a test CV file."""
    test_cv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_cvs")
    filepath = os.path.join(test_cv_dir, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    return FileResponse(filepath, filename=filename)
