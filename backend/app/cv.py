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
from utils.encryption import encrypt_text, decrypt_text
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


def extract_text_from_file(file_content: bytes, filename: str, preserve_markers: bool = True) -> tuple[str, str | None]:
    """Extract text content from uploaded file.
    
    Args:
        file_content: Raw bytes of the uploaded file
        filename: Original filename (used to detect extension)
        preserve_markers: If True, adds structural markers like [H1], [BOLD], [BULLET]
                         for better section detection. If False, returns plain text.
    
    Returns:
        tuple: (plain_text, html_content)
               - plain_text: Always present, used for AI analysis
               - html_content: For DOCX and PDF files, None for others
    """
    extension = filename.split('.')[-1].lower()
    
    # DOCX files - extract both plain text AND HTML
    if extension == 'docx':
        return _extract_docx_to_html(file_content)
    
    # DOC files (old Word format) - plain text only
    elif extension == 'doc':
        plain_text = _extract_docx_with_markers(file_content, preserve_markers)
        return (plain_text, None)
    
    # PDF files - extract both plain text AND HTML
    elif extension == 'pdf':
        return _extract_pdf_to_html(file_content)
    
    # Text/Markdown files - plain text only
    elif extension in ['txt', 'md']:
        plain_text = file_content.decode('utf-8', errors='ignore')
        return (plain_text, None)
    
    # RTF files - plain text only
    elif extension == 'rtf':
        try:
            from striprtf.striprtf import rtf_to_text
            rtf_content = file_content.decode('utf-8', errors='ignore')
            plain_text = rtf_to_text(rtf_content)
            return (plain_text, None)
        except ImportError:
            text = file_content.decode('utf-8', errors='ignore')
            text = re.sub(r'\\[a-z]+\d*\s?', '', text)
            text = re.sub(r'[{}]', '', text)
            return (text, None)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse RTF: {str(e)}")
    
    # ODT files - plain text only
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
                
                plain_text = ' '.join(text_parts)
                return (plain_text, None)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse ODT: {str(e)}")
    
    # Unknown format - try as plain text
    else:
        try:
            plain_text = file_content.decode('utf-8', errors='ignore')
            return (plain_text, None)
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
        
        # DEBUG: Analyze font sizes
        logger.info("[PDF FONT DEBUG] Analyzing font sizes...")
        font_sizes = set()
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block.get("type") == 0:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            font_sizes.add(round(span.get("size", 0), 1))
        logger.info(f"[PDF FONT DEBUG] Font sizes found: {sorted(font_sizes)}")
        logger.info(f"[PDF FONT DEBUG] Max font size: {max(font_sizes) if font_sizes else 0}")
        
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


def _extract_pdf_with_pymupdf4llm(file_content: bytes) -> tuple:
    """
    Extract text and markdown from PDF using pymupdf4llm.
    
    This provides MUCH better formatting than the old marker-based approach:
    - Proper bold detection
    - Correct bullet lists
    - Better header detection
    - Correct reading order
    
    Args:
        file_content: Raw bytes of the PDF file
        
    Returns:
        tuple: (plain_text, markdown_text)
    """
    import tempfile
    import os
    
    try:
        import pymupdf4llm
    except ImportError:
        logger.warning("[PDF] pymupdf4llm not installed, falling back to old method")
        return _extract_pdf_with_markers(file_content, preserve_markers=True), None
    
    # pymupdf4llm needs a file path, so write to temp file
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(file_content)
            temp_file = f.name
        
        # Extract to Markdown
        md_text = pymupdf4llm.to_markdown(temp_file)
        
        # Also get plain text (for AI processing - strip markdown)
        plain_text = _markdown_to_plain_text(md_text)
        
        logger.info(f"[PDF] pymupdf4llm extracted {len(md_text)} chars markdown, {len(plain_text)} chars plain")
        
        return (plain_text, md_text)
        
    except Exception as e:
        logger.warning(f"[PDF] pymupdf4llm failed: {e}, falling back to old method")
        return _extract_pdf_with_markers(file_content, preserve_markers=True), None
        
    finally:
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)


def _markdown_to_plain_text(md_text: str) -> str:
    """
    Convert Markdown to marker-format plain text for section detection.
    
    Converts markdown syntax to [H1], [H2], [BOLD], [BULLET] markers
    that block_detector.py expects.
    """
    import re
    
    if not md_text:
        return ""
    
    lines = md_text.split('\n')
    result_lines = []
    
    for line in lines:
        processed = line
        
        # Headers: # Header → [H1] Header
        if processed.strip().startswith('# '):
            processed = '[H1] ' + processed.strip()[2:]
        elif processed.strip().startswith('## '):
            processed = '[H2] ' + processed.strip()[3:]
        elif processed.strip().startswith('### '):
            processed = '[H2] ' + processed.strip()[4:]
        
        # Bullets: - item or * item → [BULLET] item
        bullet_match = re.match(r'^(\s*)[-*+]\s+(.+)$', processed)
        if bullet_match:
            indent = bullet_match.group(1)
            content = bullet_match.group(2)
            processed = f'{indent}[BULLET] {content}'
        
        # Bold: **text** → [BOLD] text (only if entire line or start of line)
        if processed.strip().startswith('**') and '**' in processed[2:]:
            bold_match = re.match(r'^\*\*(.+?)\*\*(.*)$', processed.strip())
            if bold_match:
                bold_text = bold_match.group(1)
                rest = bold_match.group(2)
                if len(bold_text) < 60 and not rest.strip().startswith('**'):
                    processed = f'[BOLD] {bold_text}{rest}'
                else:
                    processed = re.sub(r'\*\*(.+?)\*\*', r'\1', processed)
        else:
            processed = re.sub(r'\*\*(.+?)\*\*', r'\1', processed)
        
        # Strip remaining markdown (italic, links, code)
        processed = re.sub(r'\*(.+?)\*', r'\1', processed)
        processed = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', processed)
        processed = re.sub(r'`(.+?)`', r'\1', processed)
        
        result_lines.append(processed)
    
    text = '\n'.join(result_lines)
    
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def _markdown_to_clean_text(md_text: str) -> str:
    """
    Convert Markdown to clean plain text for storage and display.
    Strips all markdown syntax - NO markers.
    
    Used for cv_content storage (what users see in Section Explorer).
    """
    import re
    
    if not md_text:
        return ""
    
    text = md_text
    
    # Remove header markers (keep text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # Remove bold/italic markers (keep text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # Remove link syntax [text](url) → text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Convert bullet markers to bullet character
    text = re.sub(r'^(\s*)[-*+]\s+', r'\1• ', text, flags=re.MULTILINE)
    
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # Filter footers
    text = _filter_markdown_footers(text)
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def _markdown_to_marked_text(md_text: str) -> str:
    """
    Convert Markdown to marker-format text for detection.
    Adds [H1], [H2], [BOLD], [BULLET] markers that block_detector expects.
    
    Used only during detection - NOT stored in database.
    """
    import re
    
    if not md_text:
        return ""
    
    lines = md_text.split('\n')
    result_lines = []
    
    for line in lines:
        processed = line
        stripped = processed.strip()
        
        # Headers: # Header → [H1] Header
        if stripped.startswith('# '):
            content = stripped[2:]
            content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)
            processed = '[H1] ' + content
        elif stripped.startswith('## '):
            content = stripped[3:]
            content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)
            processed = '[H2] ' + content
        elif stripped.startswith('### '):
            content = stripped[4:]
            content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)
            processed = '[H2] ' + content
        else:
            # Bullets: - item → [BULLET] item
            bullet_match = re.match(r'^(\s*)[-*+]\s+(.+)$', processed)
            if bullet_match:
                indent = bullet_match.group(1)
                content = bullet_match.group(2)
                content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)
                processed = f'{indent}[BULLET] {content}'
            else:
                # Bold at start of line: **text** → [BOLD] text
                bold_match = re.match(r'^\*\*(.+?)\*\*(.*)$', stripped)
                if bold_match:
                    bold_text = bold_match.group(1)
                    rest = bold_match.group(2)
                    rest = re.sub(r'\*\*(.+?)\*\*', r'\1', rest)
                    if len(bold_text) < 80:
                        processed = f'[BOLD] {bold_text}{rest}'
                    else:
                        processed = f'{bold_text}{rest}'
                else:
                    processed = re.sub(r'\*\*(.+?)\*\*', r'\1', processed)
        
        # Strip remaining markdown
        processed = re.sub(r'\*(.+?)\*', r'\1', processed)
        processed = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', processed)
        processed = re.sub(r'`(.+?)`', r'\1', processed)
        
        result_lines.append(processed)
    
    text = '\n'.join(result_lines)
    
    # Filter footers
    text = _filter_markdown_footers(text)
    
    # Clean whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def _markdown_to_html(md_text: str) -> str:
    """
    Convert Markdown text to HTML for display.
    
    Converts:
    - **bold** → <strong>bold</strong>
    - *italic* → <em>italic</em>
    - # Header → <h1>Header</h1>
    - ## Header → <h2>Header</h2>
    - - item → <li>item</li>
    - [text](url) → <a href="url">text</a>
    - Paragraphs → <p>text</p>
    """
    import re
    
    if not md_text:
        return ""
    
    lines = md_text.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            continue
        
        # Convert inline formatting first
        processed = stripped
        
        # Bold: **text** → <strong>text</strong>
        processed = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', processed)
        
        # Italic: *text* → <em>text</em>
        processed = re.sub(r'\*(.+?)\*', r'<em>\1</em>', processed)
        
        # Links: [text](url) → <a href="url">text</a>
        processed = re.sub(
            r'\[([^\]]+)\]\(([^\)]+)\)', 
            r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', 
            processed
        )
        
        # Inline code: `code` → <code>code</code>
        processed = re.sub(r'`(.+?)`', r'<code>\1</code>', processed)
        
        # Headers
        if stripped.startswith('# '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            content = processed[2:]
            html_lines.append(f'<h1>{content}</h1>')
            continue
        
        if stripped.startswith('## '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            content = processed[3:]
            html_lines.append(f'<h2>{content}</h2>')
            continue
        
        if stripped.startswith('### '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            content = processed[4:]
            html_lines.append(f'<h3>{content}</h3>')
            continue
        
        # Bullet lists: - item or * item
        bullet_match = re.match(r'^[-*+]\s+(.+)$', stripped)
        if bullet_match:
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = re.sub(r'^[-*+]\s+', '', processed)
            html_lines.append(f'<li>{content}</li>')
            continue
        
        # Numbered lists: 1. item
        numbered_match = re.match(r'^\d+\.\s+(.+)$', stripped)
        if numbered_match:
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = re.sub(r'^\d+\.\s+', '', processed)
            html_lines.append(f'<li>{content}</li>')
            continue
        
        # Regular paragraph
        if in_list:
            html_lines.append('</ul>')
            in_list = False
        html_lines.append(f'<p>{processed}</p>')
    
    # Close any open list
    if in_list:
        html_lines.append('</ul>')
    
    html = '\n'.join(html_lines)
    
    # Wrap in container
    html = f'<div class="cv-html-content">{html}</div>'
    
    return html


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))


def _convert_markers_to_html(text_with_markers: str) -> str:
    """
    Convert text to HTML, detecting structure by markers OR patterns.
    
    Works with:
    - Explicit markers: [H1], [H2], [BOLD], [BULLET]
    - Pattern detection: section headers, bullets, first line as name
    """
    import re
    
    if not text_with_markers:
        return ""
    
    # Common CV section headers (lowercase for matching)
    section_headers = {
        'about', 'summary', 'profile', 'objective',
        'experience', 'work experience', 'professional experience', 'employment',
        'education', 'academic background',
        'skills', 'technical skills', 'core competencies', 'competencies',
        'certifications', 'certificates', 'licenses',
        'projects', 'key projects',
        'achievements', 'accomplishments', 'awards', 'honors',
        'languages', 'language skills',
        'interests', 'hobbies',
        'references', 'contact', 'contact information',
        'publications', 'training', 'volunteer', 'volunteering',
        'professional summary', 'career summary', 'executive summary',
        'core expertise', 'areas of expertise', 'expertise',
        'career highlights', 'highlights', 'key achievements',
        'professional affiliations', 'memberships',
    }
    
    lines = text_with_markers.split('\n')
    
    # Pre-process: Merge stray bullets with following line
    bullet_chars = {'•', '●', '○', '◦', '▪', '►', '‣', '⁃', '·', '-', '*'}
    processed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # If line is ONLY a bullet character, merge with next line
        if line in bullet_chars and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line:
                processed_lines.append(f"• {next_line}")
                i += 2
                continue
        processed_lines.append(lines[i])
        i += 1
    
    lines = processed_lines
    
    # Pre-process: Remove footer/header lines
    footer_patterns = [
        r'^Page\s+\d+\s+of\s+\d+',           # "Page 1 of 10"
        r'^Page\s+\d+$',                       # "Page 1"
        r'^\d+\s*$',                           # Just a number "1"
        r'^Page\s+\d+\s*\|',                   # "Page 1 |"
    ]
    
    cleaned_lines = []
    for line in processed_lines:
        line_stripped = line.strip()
        is_footer = False
        for pattern in footer_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                is_footer = True
                break
        if not is_footer:
            cleaned_lines.append(line)
    
    lines = cleaned_lines
    
    # DEBUG: Show processed lines with bullets
    bullet_lines = [l for l in lines if l.strip().startswith('•')]
    logger.info(f"[BULLET DEBUG] Lines starting with •: {len(bullet_lines)}")
    for bl in bullet_lines[:5]:
        logger.info(f"[BULLET DEBUG]   {bl[:60]}")
    
    html_lines = []
    in_list = False
    first_content_line = True
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        if not line:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            continue
        
        # === EXPLICIT MARKERS (highest priority) ===
        
        if line.startswith('[H1]'):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            content = line[4:].strip()
            html_lines.append(f'<h1>{_escape_html(content)}</h1>')
            first_content_line = False
            continue
        
        if line.startswith('[H2]'):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            content = line[4:].strip()
            html_lines.append(f'<h2>{_escape_html(content)}</h2>')
            first_content_line = False
            continue
        
        if line.startswith('[BOLD]'):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            content = line[6:].strip()
            html_lines.append(f'<p><strong>{_escape_html(content)}</strong></p>')
            first_content_line = False
            continue
        
        if line.startswith('[BULLET]'):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = line[8:].strip()
            html_lines.append(f'<li>{_escape_html(content)}</li>')
            first_content_line = False
            continue
        
        # === PATTERN DETECTION (when no markers) ===
        
        # First content line = likely name/title → H1
        if first_content_line:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            # Check if it looks like a header line (not too long, has name-like pattern)
            if len(line) < 100 and '|' in line:
                # Contact line with separators - make it header
                html_lines.append(f'<h1>{_escape_html(line)}</h1>')
            elif len(line) < 60:
                html_lines.append(f'<h1>{_escape_html(line)}</h1>')
            else:
                html_lines.append(f'<p>{_escape_html(line)}</p>')
            first_content_line = False
            continue
        
        # Section headers by text content
        line_lower = line.lower().strip()
        # Remove trailing colon or common suffixes for matching
        line_clean = line_lower.rstrip(':').strip()
        
        # Check exact match OR if line starts with a section header
        is_section_header = (
            line_clean in section_headers or
            any(line_clean.startswith(h + ' ') for h in section_headers) or
            any(line_clean == h + ' me' for h in ['about']) or  # "About Me"
            any(line_clean.startswith(h + ':') for h in section_headers)
        )
        
        if is_section_header:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h2>{_escape_html(line)}</h2>')
            continue
        
        # ALL CAPS short lines = likely headers
        if line.isupper() and 3 < len(line) < 40:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h2>{_escape_html(line)}</h2>')
            continue
        
        # Skip lines that are ONLY a bullet character
        if line in ['•', '●', '○', '◦', '▪', '-', '*', '►', '‣', '⁃']:
            continue
        
        # Bullet patterns
        bullet_match = re.match(r'^[•●○◦▪▸►‣⁃\-\*]\s*(.+)$', line)
        if bullet_match:
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = bullet_match.group(1)
            html_lines.append(f'<li>{_escape_html(content)}</li>')
            continue
        
        # Numbered list patterns
        numbered_match = re.match(r'^(\d+[\.\)]\s*)(.+)$', line)
        if numbered_match:
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = numbered_match.group(2)
            html_lines.append(f'<li>{_escape_html(content)}</li>')
            continue
        
        # Regular paragraph
        if in_list:
            html_lines.append('</ul>')
            in_list = False
        html_lines.append(f'<p>{_escape_html(line)}</p>')
    
    # Close any open list
    if in_list:
        html_lines.append('</ul>')
    
    html = '\n'.join(html_lines)
    html = f'<div class="cv-html-content">{html}</div>'
    
    return html


def _extract_pdf_links(file_content: bytes) -> list:
    """
    Extract hyperlinks from a PDF file.
    
    Returns:
        List of dicts: [{'text': 'LinkedIn', 'url': 'https://...'}, ...]
    """
    import fitz  # PyMuPDF
    
    links = []
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        
        for page in doc:
            page_links = page.get_links()
            
            for link in page_links:
                if link.get('uri'):  # External URL
                    url = link['uri']
                    rect = link.get('from')
                    if rect:
                        text = page.get_text("text", clip=rect).strip()
                    else:
                        text = url
                    
                    if text and url:
                        links.append({
                            'text': text,
                            'url': url
                        })
        
        doc.close()
    except Exception as e:
        logger.warning(f"[PDF] Link extraction failed: {e}")
    
    return links


def _inject_links_into_html(html: str, links: list) -> str:
    """
    Replace link text in HTML with clickable <a> tags.
    
    Args:
        html: HTML content
        links: List of {'text': ..., 'url': ...} dicts
        
    Returns:
        HTML with links converted to <a> tags
    """
    for link in links:
        text = link['text']
        url = link['url']
        
        if not url.startswith('http'):
            url = 'https://' + url
        
        escaped_text = re.escape(text)
        pattern = f'(?<!href=")(?<!>){escaped_text}(?!</a>)'
        replacement = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text}</a>'
        
        html = re.sub(pattern, replacement, html, count=1)
    
    return html


def _filter_pdf_footers(html: str) -> str:
    """
    Remove common PDF footer patterns from HTML.
    
    Removes:
    - "Page X of Y" patterns
    - "Page X | Name" patterns
    """
    import re
    
    # Remove paragraphs containing page footers
    # Match: "Page X of Y" anywhere in a paragraph
    html = re.sub(r'<p>[^<]*Page\s+\d+\s+of\s+\d+[^<]*</p>\n?', '', html, flags=re.IGNORECASE)
    
    # Match: lines that are ONLY "Page X of Y | text"
    html = re.sub(r'<p>Page\s+\d+\s+of\s+\d+\s*\|[^<]*</p>\n?', '', html, flags=re.IGNORECASE)
    
    # Also remove from list items
    html = re.sub(r'<li>[^<]*Page\s+\d+\s+of\s+\d+[^<]*</li>\n?', '', html, flags=re.IGNORECASE)
    
    return html


def _filter_markdown_footers(md_text: str) -> str:
    """
    Remove page footer lines from markdown text.
    
    Removes lines like:
    - "Page 1 of 10 | Eyal Doron CV"
    - "Page 2 of 10 **|** [Eyal Doron CV](url)"
    - Any line containing "Page X of Y"
    """
    import re
    
    if not md_text:
        return md_text
    
    lines = md_text.split('\n')
    filtered_lines = []
    
    for line in lines:
        # Skip lines containing "Page X of Y" pattern
        if re.search(r'Page\s+\d+\s+of\s+\d+', line, re.IGNORECASE):
            print(f"[PDF FILTER] Removed footer: {line[:50]}...")
            continue
        filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def _extract_pdf_to_html(file_content: bytes) -> tuple[str, str, str]:
    """
    Extract text and HTML from PDF using pymupdf4llm.
    
    Returns:
        tuple: (clean_text, html_content, marked_text)
        - clean_text: For storage in cv_content (display to users)
        - html_content: For storage in html_content (rich display)
        - marked_text: For detection only (NOT stored)
    """
    # Try pymupdf4llm first
    plain_text, md_text = _extract_pdf_with_pymupdf4llm(file_content)
    
    if md_text:
        # Filter footers from markdown first
        md_text = _filter_markdown_footers(md_text)
        
        # Generate all three outputs
        html_content = _markdown_to_html(md_text)
        clean_text = _markdown_to_clean_text(md_text)
        marked_text = _markdown_to_marked_text(md_text)
        
        print(f"[PDF] Generated: clean={len(clean_text)}, html={len(html_content)}, marked={len(marked_text)}")
        
        return (clean_text, html_content, marked_text)
    
    # Fallback to old method
    print("[PDF] Using fallback marker-based extraction")
    text_with_markers = _extract_pdf_with_markers(file_content, preserve_markers=True)
    html_content = _convert_markers_to_html(text_with_markers)
    
    # For fallback: text already has markers, strip for clean version
    from common.detection.block_detector import strip_structure_markers
    clean_text = strip_structure_markers(text_with_markers)
    
    return (clean_text, html_content, text_with_markers)


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
    # Also extract HTML for rich display (DOCX files only)
    text_with_markers, html_content = extract_text_from_file(file_content, file.filename, preserve_markers=True)
    
    # Check content length using clean text (without markers) for accurate count
    clean_text = strip_structure_markers(text_with_markers)
    
    if not clean_text or len(clean_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Could not extract sufficient text from file")
    
    # Store WITH markers for detection - markers stripped at display time
    # This enables better section detection during CV analysis
    encrypted_content = encrypt_text(text_with_markers)
    
    # Encrypt HTML content if available (for DOCX files)
    encrypted_html = encrypt_text(html_content) if html_content else None
    
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """INSERT INTO user_cvs (user_id, filename, original_filename, content, html_content, file_size, file_type)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (str(user["id"]), file.filename, file.filename, encrypted_content, encrypted_html, len(file_content), extension)
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
            """SELECT id, filename, file_type, file_size, content, html_content, created_at FROM user_cvs 
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
            "content": decrypt_text(cv["content"]) if cv["content"] else None,
            "html_content": decrypt_text(cv["html_content"]) if cv["html_content"] else None,
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
