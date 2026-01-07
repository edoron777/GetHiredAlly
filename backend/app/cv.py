"""CV upload and management endpoints."""
import os
import sys
import io
import re
import logging
import hashlib
import psycopg2
import mammoth
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


def extract_text_from_file(file_content: bytes, filename: str, preserve_markers: bool = True) -> str:
    """Extract text content from uploaded file.
    
    Args:
        file_content: Raw bytes of the uploaded file
        filename: Original filename (used to detect extension)
        preserve_markers: If True, adds structural markers like [H1], [BOLD], [BULLET]
                         for better section detection. If False, returns plain text.
    
    Returns:
        Extracted text, optionally with structure markers
    """
    extension = filename.split('.')[-1].lower()
    
    if extension == 'txt':
        return file_content.decode('utf-8', errors='ignore')
    
    elif extension == 'pdf':
        return _extract_pdf_with_markers(file_content, preserve_markers)
    
    elif extension in ['docx', 'doc']:
        return _extract_docx_with_markers(file_content, preserve_markers)
    
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


def _extract_pdf_with_markers(file_content: bytes, preserve_markers: bool = True) -> str:
    """Extract PDF text using PyMuPDF with optional structure markers.
    
    Markers added:
    - [H1] for text with font size > 14pt
    - [H2] for text with font size > 12pt  
    - [BOLD] for bold text (potential headers)
    """
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(stream=file_content, filetype="pdf")
        result_lines = []
        
        for page in doc:
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
            
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    block_lines = []
                    
                    for line in block.get("lines", []):
                        line_text = ""
                        line_is_header = False
                        max_font_size = 0
                        
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if not text:
                                continue
                            
                            font_size = span.get("size", 12)
                            font_name = span.get("font", "").lower()
                            is_bold = "bold" in font_name or "black" in font_name
                            
                            max_font_size = max(max_font_size, font_size)
                            
                            if preserve_markers:
                                if font_size > 14 or (font_size > 12 and is_bold):
                                    line_is_header = True
                            
                            line_text += text + " "
                        
                        line_text = line_text.strip()
                        if line_text:
                            if preserve_markers and line_is_header:
                                if max_font_size > 14:
                                    result_lines.append(f"[H1] {line_text}")
                                else:
                                    result_lines.append(f"[H2] {line_text}")
                            else:
                                result_lines.append(line_text)
            
            result_lines.append("")  # Page break
        
        doc.close()
        return '\n'.join(result_lines)
        
    except Exception as e:
        logger.warning(f"PyMuPDF extraction failed, falling back to pdfplumber: {e}")
        # Fallback to pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                return '\n'.join(text_parts)
        except Exception as e2:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e2)}")


def _extract_docx_with_markers(file_content: bytes, preserve_markers: bool = True) -> str:
    """Extract DOCX text with optional structure markers.
    
    Markers added:
    - [H1] for Heading 1 style or font size > 14pt
    - [H2] for Heading 2/3 style or font size > 12pt
    - [BOLD] for fully bold paragraphs (potential headers)
    - [BULLET] for list items
    """
    try:
        from docx import Document
        from docx.opc.constants import RELATIONSHIP_TYPE as RT
        
        doc = Document(io.BytesIO(file_content))
        result_lines = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                result_lines.append("")  # Preserve blank lines for structure
                continue
            
            markers = []
            
            if preserve_markers:
                # Check 1: Heading styles
                style_name = para.style.name if para.style else ""
                if style_name and ("Heading 1" in style_name or "Title" in style_name):
                    markers.append("H1")
                elif style_name and "Heading" in style_name:
                    markers.append("H2")
                
                # Check 2: All runs are bold (likely a header)
                runs_with_text = [r for r in para.runs if r.text.strip()]
                if runs_with_text:
                    all_bold = all(r.bold for r in runs_with_text)
                    if all_bold and "H1" not in markers and "H2" not in markers:
                        markers.append("BOLD")
                
                # Check 3: Large font size
                for run in para.runs:
                    if run.font.size:
                        size_pt = run.font.size.pt
                        if size_pt > 14 and "H1" not in markers:
                            markers.append("H1")
                            break
                        elif size_pt > 12 and "H1" not in markers and "H2" not in markers:
                            markers.append("H2")
                            break
                
                # Check 4: List item (bullet/numbered)
                try:
                    if para._element.pPr is not None:
                        numPr = para._element.pPr.numPr
                        if numPr is not None:
                            markers.append("BULLET")
                except:
                    pass
                
                # Check 5: ALL CAPS short text (likely header)
                if len(text) < 50 and text.isupper() and not markers:
                    markers.append("BOLD")
            
            # Format output with markers
            if markers:
                # Use highest priority marker
                if "H1" in markers:
                    result_lines.append(f"[H1] {text}")
                elif "H2" in markers:
                    result_lines.append(f"[H2] {text}")
                elif "BOLD" in markers:
                    result_lines.append(f"[BOLD] {text}")
                elif "BULLET" in markers:
                    result_lines.append(f"[BULLET] {text}")
                else:
                    result_lines.append(text)
            else:
                result_lines.append(text)
        
        # Extract hyperlinks
        relevant_domains = ['linkedin.com', 'github.com', 'gitlab.com', 'bitbucket.org', 'portfolio', 'behance.net', 'dribbble.com']
        hyperlinks = set()
        try:
            for rel in doc.part.rels.values():
                if rel.reltype == RT.HYPERLINK and rel.target_ref:
                    link = str(rel.target_ref).lower()
                    if any(domain in link for domain in relevant_domains):
                        hyperlinks.add(rel.target_ref)
        except:
            pass
        
        text = '\n'.join(result_lines)
        
        if hyperlinks:
            text += "\n\n[HYPERLINKS FOUND IN DOCUMENT:]\n"
            for link in sorted(hyperlinks):
                text += f"- {link}\n"
        
        return text
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse DOCX: {str(e)}")


# ============================================================
# HTML Extraction with mammoth (Phase 2 - TextStylerService)
# ============================================================

def _extract_docx_to_html(file_content: bytes) -> tuple[str, str]:
    """
    Extract both plain text AND HTML from a DOCX file.
    
    Uses mammoth for HTML extraction (preserves formatting).
    Uses python-docx for plain text extraction (for AI analysis).
    
    Args:
        file_content: Raw bytes of the DOCX file
        
    Returns:
        tuple: (plain_text, html_content)
               - plain_text: Text with [MARKERS] for AI analysis
               - html_content: Semantic HTML for display
               
    If mammoth fails, returns (plain_text, None)
    """
    # Step 1: Extract plain text using existing function (for AI analysis)
    plain_text = _extract_docx_with_markers(file_content, preserve_markers=True)
    
    # Step 2: Extract HTML using mammoth (for display)
    html_content = None
    try:
        # mammoth style mapping for clean semantic HTML
        style_map = """
            p[style-name='Heading 1'] => h1:fresh
            p[style-name='Heading 2'] => h2:fresh
            p[style-name='Heading 3'] => h3:fresh
            p[style-name='Title'] => h1.title:fresh
            b => strong
            i => em
            u => u
            strike => s
        """
        
        result = mammoth.convert_to_html(
            io.BytesIO(file_content),
            style_map=style_map
        )
        
        html_content = result.value
        
        # Log any conversion messages (warnings, not errors)
        if result.messages:
            for message in result.messages:
                logger.info(f"[mammoth] {message.type}: {message.message}")
        
        # Post-process HTML for better display
        html_content = _post_process_html(html_content)
        
    except Exception as e:
        # Log error but don't fail - fall back to plain text only
        logger.warning(f"[mammoth] HTML extraction failed: {str(e)}")
        html_content = None
    
    return (plain_text, html_content)


def _post_process_html(html: str) -> str:
    """
    Post-process mammoth HTML output for better display.
    
    - Adds CSS classes for styling
    - Cleans up empty paragraphs
    - Ensures proper structure
    """
    if not html:
        return html
    
    # Remove empty paragraphs
    html = html.replace('<p></p>', '')
    
    # Add wrapper div with class for styling
    html = f'<div class="cv-html-content">{html}</div>'
    
    # Clean up excessive whitespace
    html = re.sub(r'\s+', ' ', html)
    html = html.replace('> <', '><')
    
    return html.strip()


def strip_structure_markers(text: str) -> str:
    """Convert structure markers to visible fallback characters for plain text display.
    
    Converts markers to visible equivalents so formatting is preserved in plain text mode:
    - [BULLET] -> "• " (bullet character)
    - [BOLD]...[/BOLD] -> **...** (markdown bold)
    - [H1], [H2] -> removed (text preserved)
    """
    # Replace [BULLET] with visible bullet character
    text = re.sub(r'^\[BULLET\]\s*', '• ', text, flags=re.MULTILINE)
    # Remove [H1], [H2] markers (keep text)
    text = re.sub(r'^\[(H1|H2)\]\s*', '', text, flags=re.MULTILINE)
    # Replace line-start [BOLD] with nothing (handled by inline below)
    text = re.sub(r'^\[BOLD\]\s*', '', text, flags=re.MULTILINE)
    # Convert inline [BOLD]...[/BOLD] to markdown **...** for plain text
    text = re.sub(r'\[BOLD\](.*?)\[/BOLD\]', r'**\1**', text)
    # Clean up any remaining orphaned markers
    text = text.replace('[BOLD]', '').replace('[/BOLD]', '')
    return text


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
    
    # Extract text WITH markers for better detection during scanning
    # Markers like [H1], [BOLD], [BULLET] help detect section headers
    text_with_markers = extract_text_from_file(file_content, file.filename, preserve_markers=True)
    
    # Check content length using clean text (without markers) for accurate count
    clean_text = strip_structure_markers(text_with_markers)
    
    if not clean_text or len(clean_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Could not extract sufficient text from file")
    
    # Store WITH markers for detection - markers stripped at display time
    # This enables better section detection during CV analysis
    encrypted_content = encrypt_text(text_with_markers)
    
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
            "content_length": len(clean_text)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save CV: {str(e)}")


@router.get("/section-guides")
async def get_section_guides(token: str = None):
    """
    Get all CV section guide content for Guide Mode.
    Returns educational content for each CV section.
    """
    user = get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not available")
        
        response = supabase.table("cv_section_guides") \
            .select("*") \
            .eq("is_active", True) \
            .order("display_order") \
            .execute()
        
        if response.data:
            return response.data
        else:
            return []
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching section guides: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch section guides")


@router.get("/section-guides/{section_key}")
async def get_section_guide(section_key: str, token: str = None):
    """
    Get guide content for a specific CV section.
    """
    user = get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not available")
        
        response = supabase.table("cv_section_guides") \
            .select("*") \
            .eq("section_key", section_key.upper()) \
            .eq("is_active", True) \
            .single() \
            .execute()
        
        if response.data:
            return response.data
        else:
            raise HTTPException(status_code=404, detail=f"No guide found for section: {section_key}")
            
    except HTTPException:
        raise
    except Exception as e:
        if "No rows" in str(e) or "0 rows" in str(e):
            raise HTTPException(status_code=404, detail=f"No guide found for section: {section_key}")
        logger.error(f"Error fetching section guide: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch section guide")


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


@router.get("/dev/analyze-structure/{scan_id}")
async def analyze_cv_structure(scan_id: str, token: str = None):
    """DEV ONLY: Return detailed block structure analysis for debugging.
    
    Note: scan_id is the ID from cv_scan_results table (numeric), 
    NOT the user_cvs.id (UUID). This matches what the frontend passes.
    """
    from common.detection.block_detector import detect_cv_blocks, BlockType
    from utils.encryption import decrypt_text, is_encrypted
    
    user = get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT original_cv_content FROM cv_scan_results WHERE id = %s AND user_id = %s",
            (scan_id, str(user["id"]))
        )
        scan = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not scan or not scan.get("original_cv_content"):
            raise HTTPException(status_code=404, detail="Scan not found")
        
        cv_text = scan["original_cv_content"]
        
        if is_encrypted(cv_text):
            cv_text = decrypt_text(cv_text)
        
        block_structure = detect_cv_blocks(cv_text)
        
        result = {
            "total_blocks": len(block_structure.blocks),
            "total_jobs": len(block_structure.all_jobs),
            "total_bullets": len(block_structure.all_bullets),
            "total_education": len(block_structure.all_education),
            "total_certifications": len(block_structure.all_certifications),
            "processing_time_ms": round(block_structure.processing_time_ms, 2),
            "blocks": []
        }
        
        for block in block_structure.blocks:
            block_info = {
                "type": block.block_type.value if hasattr(block.block_type, 'value') else str(block.block_type),
                "start_line": block.start_line,
                "end_line": block.end_line,
                "word_count": block.word_count,
                "content_preview": block.content[:150] + "..." if len(block.content) > 150 else block.content
            }
            
            if block.block_type == BlockType.EXPERIENCE and block.jobs:
                block_info["jobs"] = [{
                    "title": job.job_title,
                    "company": job.company_name,
                    "dates": job.dates,
                    "duration_months": job.duration_months,
                    "bullet_count": len(job.bullets),
                    "lines": f"{job.start_line}-{job.end_line}"
                } for job in block.jobs]
            
            if block.block_type == BlockType.EDUCATION and block.education_entries:
                block_info["entries"] = [{
                    "degree": entry.degree,
                    "institution": entry.institution,
                    "year": entry.graduation_year
                } for entry in block.education_entries]
            
            if block.block_type == BlockType.CERTIFICATIONS and block.certifications:
                block_info["certs"] = [cert.name for cert in block.certifications]
            
            result["blocks"].append(block_info)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
