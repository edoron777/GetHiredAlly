"""CV Optimizer scanning and analysis endpoints."""
import os
import re
import sys
import json
import hashlib
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from io import BytesIO
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from supabase import create_client, Client

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ai_service import generate_completion
from utils.encryption import decrypt_text
from utils.file_generators import generate_pdf, generate_docx
from config.rate_limiter import limiter
from common.scoring import calculate_cv_score as calculate_cv_score_new, calculate_after_fix_score, get_score_message
from common.scoring.extractors import extract_patterns, analyze_text
from common.scoring.severity import assign_severity_to_issues, count_issues_by_severity
from common.detection import detect_cv_issues, CVIssueReport
from common.detection.changes_extractor import extract_changes_code_based
from common.detection.block_detector import strip_structure_markers
from common.utils.marker_converter import convert_markers_to_html

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cv-optimizer", tags=["cv-optimizer"])


def calculate_cv_score_from_issues(issues: list) -> dict:
    """
    Calculate CV score based on issues found (fallback method).
    Score is deterministic - same issues = same score.
    
    Scoring weights:
    - Critical issues: -15 points each (major problems)
    - High issues: -8 points each (significant issues)
    - Medium issues: -3 points each (improvements)
    - Low issues: -1 point each (polish)
    
    Base score: 100
    Minimum score: 10 (never show 0)
    """
    base_score = 100
    
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    
    for issue in issues:
        severity = issue.get('severity', 'low').lower() if isinstance(issue, dict) else 'low'
        if severity in ['critical', 'quick_wins']:
            critical_count += 1
        elif severity in ['high', 'important']:
            high_count += 1
        elif severity in ['medium', 'consider']:
            medium_count += 1
        elif severity in ['low', 'polish']:
            low_count += 1
    
    penalty = (
        (critical_count * 15) +
        (high_count * 8) +
        (medium_count * 3) +
        (low_count * 1)
    )
    
    final_score = base_score - penalty
    final_score = max(10, min(100, final_score))
    
    if final_score >= 85:
        message = "Excellent! Your CV is highly polished."
        status = "excellent"
    elif final_score >= 70:
        message = "Good CV with minor improvements possible."
        status = "good"
    elif final_score >= 55:
        message = "Decent CV. Some improvements recommended."
        status = "decent"
    elif final_score >= 40:
        message = "Your CV needs attention in several areas."
        status = "needs_work"
    else:
        message = "Significant improvements needed for best results."
        status = "needs_improvement"
    
    logger.info(f"[CV_SCORE] Critical: {critical_count}×15={critical_count*15}, High: {high_count}×8={high_count*8}, Medium: {medium_count}×3={medium_count*3}, Low: {low_count}×1={low_count*1}, Penalty: {penalty}, Score: {final_score}")
    
    return {
        'score': final_score,
        'message': message,
        'status': status,
        'breakdown': {
            'critical_issues': critical_count,
            'high_issues': high_count,
            'medium_issues': medium_count,
            'low_issues': low_count,
            'total_penalty': penalty
        }
    }


def extract_cv_data_and_score(cv_text: str) -> dict:
    """Extract CV features and calculate deterministic score using new scoring module."""
    patterns = extract_patterns(cv_text)
    text_metrics = analyze_text(cv_text)
    
    extracted_data = {
        "contact": {
            "has_name": True,
            "has_email": patterns.get("has_email", False),
            "has_phone": patterns.get("has_phone", False),
            "has_linkedin": patterns.get("has_linkedin", False),
            "email_is_professional": True,
        },
        "structure": {
            "has_section_headers": patterns.get("has_section_headers", False),
            "uses_bullet_points": text_metrics.get("total_bullet_points", 0) > 0,
            "has_skills_section": True,
            "skills_are_categorized": False,
            "page_count": text_metrics.get("estimated_page_count", 1),
            "word_count": text_metrics.get("word_count", 0),
        },
        "quantification": {
            "total_bullet_points": text_metrics.get("total_bullet_points", 0),
            "bullets_with_numbers": patterns.get("bullets_with_numbers", 0),
        },
        "language": {
            "strong_action_verbs_count": patterns.get("strong_action_verbs_count", 0),
            "weak_phrases_count": patterns.get("weak_phrases_count", 0),
            "passive_voice_count": patterns.get("passive_voice_count", 0),
        },
        "grammar": {
            "grammar_errors_count": 0,
            "spelling_errors_count": 0,
        },
        "experience": {
            "has_dates_for_each_role": True,
            "dates_are_consistent_format": True,
            "is_reverse_chronological": True,
            "has_company_names": True,
            "has_job_titles": True,
        },
        "keywords": {
            "tech_keywords_found": [],
        }
    }
    
    score_result = calculate_cv_score_new(extracted_data)
    
    logger.info(f"[CV_SCORE_NEW] Score: {score_result.total_score}, Grade: {score_result.grade_label}, Breakdown: {score_result.breakdown}")
    
    return {
        'score': score_result.total_score,
        'message': get_score_message(score_result.total_score),
        'status': score_result.grade_label.lower().replace(' ', '_'),
        'breakdown': score_result.breakdown,
        'version': '4.0.0'
    }


def get_db_connection():
    """Get direct PostgreSQL connection using individual params to handle special chars in password."""
    from urllib.parse import urlparse, unquote
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
    except Exception:
        return None


def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def get_user_from_token(token: str) -> dict | None:
    """Get user from session token using direct database connection."""
    if not token:
        return None
    
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to get database connection")
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
        logger.error(f"Database error: {str(e)}")
        return None


CV_ANALYSIS_PROMPT = """You are a CV/Resume expert with 20 years of experience in HR and recruitment.
Analyze this CV thoroughly and identify ALL issues that could hurt the candidate's chances.

For each issue found, return a JSON object with:
- id: sequential number
- issue: brief description of the problem
- issue_type: MUST be one of the EXACT values listed below
- category: one of the categories below
- location: where in the CV (section name)
- current_text: the exact problematic text (quote it)
- suggested_fix: how to fix it with example
- fix_difficulty: "quick" | "medium" | "complex"
- is_auto_fixable: true/false (can AI fix this without human input?)

ISSUE_TYPE VALUES - Use EXACTLY one of these (do NOT invent new types):

CRITICAL ISSUES (will cause immediate rejection):
"SPELLING_ERROR", "GRAMMAR_ERROR", "MISSING_EMAIL", "MISSING_PHONE", 
"INVALID_EMAIL", "INVALID_PHONE"

HIGH PRIORITY (major competitive disadvantage):
"NO_METRICS", "WEAK_ACTION_VERBS", "EMPLOYMENT_GAP", "MISSING_LINKEDIN",
"VAGUE_DESCRIPTION", "NO_ACHIEVEMENTS", "MISSING_DATES", "MISSING_COMPANY",
"MISSING_TITLE", "BUZZWORD_STUFFING"

MEDIUM PRIORITY (optimization opportunity):
"FORMAT_INCONSISTENT", "WEAK_SUMMARY", "SECTION_ORDER", "ATS_INCOMPATIBLE",
"BULLET_FORMAT", "MISSING_KEYWORDS", "DATE_FORMAT_INCONSISTENT",
"CONTACT_INCOMPLETE", "SKILLS_UNORGANIZED", "REPETITIVE_CONTENT"

LOW PRIORITY (minor polish):
"CV_TOO_LONG", "CV_TOO_SHORT", "BULLET_TOO_LONG", "BULLET_TOO_SHORT",
"WHITESPACE_ISSUE", "MINOR_FORMAT", "HEADER_STYLE", "OUTDATED_INFO"

IMPORTANT: Use EXACTLY one of these issue_type values. Do NOT invent new types.
Do NOT include a "severity" field - severity will be assigned by the system.

IS_AUTO_FIXABLE RULES:

Set is_auto_fixable: true for issues that can be fixed by rewriting text:
- Grammar errors (spelling, punctuation, typos)
- Weak action verbs ("responsible for", "worked on", "helped with")
- Missing quantification (AI can add realistic estimates like "20%", "15+ projects")
- Passive voice sentences
- Vague or generic descriptions
- Formatting issues in text content
- Unprofessional language
- Redundant or wordy phrases

Set is_auto_fixable: false for issues requiring human input:
- Missing contact information (email, phone, address)
- Missing entire sections (education dates, work experience)
- Incorrect or unverifiable dates
- Missing specific certifications or credentials
- Personal information only the user knows
- Missing company names or job titles

DEFAULT: When in doubt, set is_auto_fixable: true

EMAIL ADDRESS RULES:
- Do NOT flag standard email providers (Gmail, Outlook, Yahoo, Hotmail) as unprofessional
- Gmail addresses like "firstname.lastname@gmail.com" or "firstnamelastname@gmail.com" are ACCEPTABLE
- ONLY flag email addresses that contain:
  * Nicknames or inappropriate words (e.g., coolDude@, partyGirl@, gamerBoy@)
  * Numbers that look like birth years (e.g., john1985@, mike1990@)
  * Very long or confusing combinations
  * Unprofessional language

LINKEDIN/GITHUB URL RULES:
- If you see text like "LinkedIn" or "GitHub" but no visible URL, check the HYPERLINKS section at the end
- If a linkedin.com or github.com URL exists in HYPERLINKS, do NOT flag as "Missing LinkedIn/GitHub URL"
- Only flag missing links if no URL is found anywhere in the document

CATEGORIES:
1. Spelling & Grammar
2. Formatting & Structure
3. Missing Information
4. Weak Presentation
5. Lack of Quantification
6. Employment Gaps
7. CV Length
8. Tech-Specific
9. Tailoring
10. Career Narrative
11. Personal Information

Be thorough! Find every issue, even small ones. Better to over-report than miss something.

CV CONTENT:
---
{cv_content}
---

Return ONLY a valid JSON array of issues. No other text. Example:
[
  {{"id": 1, "issue": "Spelling error", "issue_type": "SPELLING_ERROR", "category": "Spelling & Grammar", "location": "Professional Summary", "current_text": "Developped", "suggested_fix": "Developed", "fix_difficulty": "quick", "is_auto_fixable": true}},
  {{"id": 2, "issue": "Missing email", "issue_type": "MISSING_EMAIL", "category": "Missing Information", "location": "Contact Section", "current_text": "Phone only listed", "suggested_fix": "Add professional email like firstname.lastname@email.com", "fix_difficulty": "quick", "is_auto_fixable": false}}
]
"""


def parse_ai_json_response(response_text: str) -> list:
    """Robust JSON parsing that handles markdown code fences, extra text, and truncation."""
    text = response_text.strip()
    
    # Remove markdown code fences if present
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    # Try direct parse first
    try:
        result = json.loads(text)
        return result
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON array in the text
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end > start:
        json_text = text[start:end + 1]
        try:
            result = json.loads(json_text)
            return result
        except json.JSONDecodeError:
            # JSON might be truncated - try to fix it
            logger.info("[CV_SCAN] JSON truncated, attempting to fix...")
            fixed_json = fix_truncated_json(json_text)
            try:
                result = json.loads(fixed_json)
                logger.info(f"[CV_SCAN] Successfully fixed truncated JSON, recovered {len(result)} issues")
                return result
            except json.JSONDecodeError as e:
                logger.warning(f"[CV_SCAN] Fix attempt failed: {e}")
                raise
    
    # If no closing bracket found, response might be severely truncated
    if start != -1:
        json_text = text[start:]
        logger.info("[CV_SCAN] No closing bracket found, attempting to fix severely truncated JSON...")
        fixed_json = fix_truncated_json(json_text)
        try:
            result = json.loads(fixed_json)
            logger.info(f"[CV_SCAN] Successfully recovered {len(result)} issues from truncated response")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"[CV_SCAN] Severe truncation fix failed: {e}")
    
    raise json.JSONDecodeError("No valid JSON array found", text, 0)


def clean_markdown_for_analysis(text: str) -> str:
    """Strip Markdown formatting symbols for cleaner AI analysis.
    
    This prevents the AI from flagging markdown syntax (*, **, #, etc.) 
    as formatting issues when analyzing .md files.
    """
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', lambda m: m.group(0).strip('`'), text)
    
    # Remove headers (# ## ###) but keep the text
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold/italic markers but keep the text
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)  # Bold+italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)       # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)           # Italic
    text = re.sub(r'___(.+?)___', r'\1', text)         # Bold+italic underscore
    text = re.sub(r'__(.+?)__', r'\1', text)           # Bold underscore
    text = re.sub(r'_(.+?)_', r'\1', text)             # Italic underscore
    
    # Remove link syntax but keep text [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove image syntax ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
    
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # Remove list markers but keep content
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def fix_truncated_json(json_text: str) -> str:
    """Attempt to fix truncated JSON array by finding last complete object."""
    text = json_text.rstrip()
    
    # Strategy: Find all complete JSON objects and keep only those
    # A complete object ends with } and has balanced quotes before it
    
    # First, try to find the last complete object by looking for },
    # but we need to ensure the object before it is actually complete
    
    # Find all positions where we have a complete object (ends with })
    # by iterating backwards and finding properly closed objects
    
    complete_objects = []
    depth = 0
    in_string = False
    escape_next = False
    current_start = -1
    
    i = 0
    while i < len(text):
        char = text[i]
        
        if escape_next:
            escape_next = False
            i += 1
            continue
            
        if char == '\\' and in_string:
            escape_next = True
            i += 1
            continue
            
        if char == '"' and not escape_next:
            in_string = not in_string
            
        if not in_string:
            if char == '[' and depth == 0:
                pass  # Skip the opening bracket
            elif char == '{':
                if depth == 0:
                    current_start = i
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and current_start != -1:
                    # Found a complete object
                    complete_objects.append((current_start, i + 1))
                    current_start = -1
        
        i += 1
    
    # If we found complete objects, reconstruct the array with only those
    if complete_objects:
        objects_text = [text[start:end] for start, end in complete_objects]
        result = '[' + ','.join(objects_text) + ']'
        return result
    
    # Fallback: try the old method
    # Find the last complete object marker },
    last_complete = text.rfind('},')
    if last_complete != -1:
        text = text[:last_complete + 1]
    else:
        # Try to find last complete object without comma
        last_complete = text.rfind('}')
        if last_complete != -1:
            # Make sure this } closes an object, not just any brace
            text = text[:last_complete + 1]
    
    # Ensure we start with [ and end with ]
    if not text.startswith('['):
        start_bracket = text.find('[')
        if start_bracket != -1:
            text = text[start_bracket:]
        else:
            text = '[' + text
    
    if not text.endswith(']'):
        text = text.rstrip(',') + ']'
    
    return text


async def analyze_cv_with_ai(cv_content: str, user_id: str, is_markdown: bool = False) -> dict:
    """
    Analyze CV using STATIC detection (deterministic).
    
    NEW FLOW:
    1. CODE detects issues (detect_all_issues) - DETERMINISTIC
    2. CODE assigns severity (assign_severity_to_issues) - DETERMINISTIC
    3. Same CV text → Same issues → Same results (ALWAYS)
    
    AI is NO LONGER used for issue detection.
    """
    if is_markdown:
        cv_content = clean_markdown_for_analysis(cv_content)
        logger.info("[CV_SCAN] Cleaned markdown formatting from CV content")
    
    try:
        logger.info("[CV_SCAN] Starting STATIC issue detection (deterministic)...")
        
        # Use new detect_cv_issues() for enhanced reporting
        report = detect_cv_issues(cv_content)
        issues = report.issues  # Same List[Dict] format for backward compatibility
        
        # Log enhanced metrics
        logger.info(f"[CV_SCAN] Static detection: Score={report.summary.overall_score}/100, Issues={report.summary.total_issues}")
        
        for i, issue in enumerate(issues):
            issue['id'] = i + 1
            if 'issue' not in issue and 'description' in issue:
                issue['issue'] = issue['description']
            if 'category' not in issue:
                issue['category'] = _get_category_for_issue_type(issue.get('issue_type', ''))
            if 'fix_difficulty' not in issue:
                issue['fix_difficulty'] = _get_fix_difficulty(issue.get('issue_type', ''))
            if 'is_auto_fixable' not in issue:
                issue['is_auto_fixable'] = _is_auto_fixable(issue.get('issue_type', ''))
            if 'current' in issue and 'current_text' not in issue:
                issue['current_text'] = issue['current']
        
        logger.info(f"[CV_SCAN] Static detection complete. Total issues: {len(issues)}")
        
        return {
            'issues': issues,
            'detection_method': 'static'
        }
        
    except Exception as e:
        logger.error(f"[CV_SCAN] Static detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CV analysis failed: {str(e)}")


def _get_category_for_issue_type(issue_type: str) -> str:
    """Map issue_type to category for frontend display."""
    category_map = {
        'SPELLING_ERROR': 'Spelling & Grammar',
        'GRAMMAR_ERROR': 'Spelling & Grammar',
        'MISSING_EMAIL': 'Missing Information',
        'MISSING_PHONE': 'Missing Information',
        'MISSING_LINKEDIN': 'Missing Information',
        'INVALID_EMAIL': 'Missing Information',
        'INVALID_PHONE': 'Missing Information',
        'NO_METRICS': 'Lack of Quantification',
        'WEAK_ACTION_VERBS': 'Weak Presentation',
        'VAGUE_DESCRIPTION': 'Weak Presentation',
        'BUZZWORD_STUFFING': 'Weak Presentation',
        'WEAK_SUMMARY': 'Formatting & Structure',
        'SECTION_ORDER': 'Formatting & Structure',
        'FORMAT_INCONSISTENT': 'Formatting & Structure',
        'DATE_FORMAT_INCONSISTENT': 'Formatting & Structure',
        'BULLET_FORMAT': 'Formatting & Structure',
        'BULLET_TOO_LONG': 'CV Length',
        'BULLET_TOO_SHORT': 'CV Length',
        'CV_TOO_LONG': 'CV Length',
        'CV_TOO_SHORT': 'CV Length',
        'WHITESPACE_ISSUE': 'Formatting & Structure',
        'MINOR_FORMAT': 'Formatting & Structure',
        'HEADER_STYLE': 'Formatting & Structure',
        'OUTDATED_INFO': 'Career Narrative',
        'REPETITIVE_CONTENT': 'Weak Presentation',
    }
    return category_map.get(issue_type, 'Other')


def _get_fix_difficulty(issue_type: str) -> str:
    """Determine fix difficulty based on issue type."""
    quick_fixes = ['SPELLING_ERROR', 'GRAMMAR_ERROR', 'WHITESPACE_ISSUE', 'MINOR_FORMAT']
    complex_fixes = ['MISSING_EMAIL', 'MISSING_PHONE', 'CV_TOO_SHORT', 'SECTION_ORDER']
    
    if issue_type in quick_fixes:
        return 'quick'
    elif issue_type in complex_fixes:
        return 'complex'
    return 'medium'


def _is_auto_fixable(issue_type: str) -> bool:
    """Determine if issue can be auto-fixed by AI."""
    auto_fixable = [
        'SPELLING_ERROR', 'GRAMMAR_ERROR', 'WEAK_ACTION_VERBS', 
        'VAGUE_DESCRIPTION', 'BUZZWORD_STUFFING', 'NO_METRICS',
        'BULLET_FORMAT', 'WEAK_SUMMARY', 'REPETITIVE_CONTENT'
    ]
    return issue_type in auto_fixable


class ScanRequest(BaseModel):
    cv_id: str
    token: str


@router.post("/scan")
@limiter.limit("10/hour")
async def scan_cv(request: Request, scan_request: ScanRequest):
    user = get_user_from_token(scan_request.token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT * FROM user_cvs WHERE id = %s AND user_id = %s""",
            (scan_request.cv_id, str(user["id"]))
        )
        cv = cursor.fetchone()

        if not cv:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="CV not found")

        cv_content = cv.get("content", "")

        if cv_content:
            try:
                cv_content = decrypt_text(cv_content)
            except Exception:
                pass

        if not cv_content or len(cv_content.strip()) < 50:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="CV content is too short or empty")

        # Check if file is markdown based on filename OR content patterns
        filename = cv.get("file_name", "") or ""
        is_markdown = (
            filename.lower().endswith('.md') or 
            filename.lower().endswith('.markdown') or
            # Detect markdown by common patterns in content
            bool(re.search(r'^#{1,6}\s+', cv_content, re.MULTILINE)) or  # Headers
            bool(re.search(r'\*\*[^*]+\*\*', cv_content)) or  # Bold
            bool(re.search(r'\[[^\]]+\]\([^)]+\)', cv_content))  # Links
        )
        
        analysis_result = await analyze_cv_with_ai(cv_content, str(user["id"]), is_markdown=is_markdown)

        issues = analysis_result.get('issues', [])
        summary = {
            'critical': len([i for i in issues if i.get('severity') == 'critical']),
            'high': len([i for i in issues if i.get('severity') == 'high']),
            'medium': len([i for i in issues if i.get('severity') == 'medium']),
            'low': len([i for i in issues if i.get('severity') == 'low']),
            'total': len(issues)
        }

        cursor.execute(
            """INSERT INTO cv_scan_results 
               (user_id, cv_id, total_issues, critical_count, high_count, medium_count, low_count, original_cv_content, issues_json, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (str(user["id"]), scan_request.cv_id, summary['total'], summary['critical'], 
             summary['high'], summary['medium'], summary['low'], cv_content, json.dumps(issues), 'completed')
        )
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=500, detail="Failed to save scan results")

        scan_id = result["id"]
        score_data = extract_cv_data_and_score(cv_content) if cv_content else calculate_cv_score_from_issues(issues)

        return {
            'scan_id': scan_id,
            'summary': summary,
            'issues': issues,
            'cv_score': score_data['score'],
            'score_message': score_data['message'],
            'score_status': score_data['status'],
            'score_breakdown': score_data['breakdown']
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("/results/{scan_id}")
async def get_scan_results(scan_id: str, token: str):
    """Get scan results summary (for summary page)."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT id, user_id, cv_id, scan_date, total_issues, critical_count, high_count, medium_count, low_count, status
               FROM cv_scan_results WHERE id = %s AND user_id = %s""",
            (scan_id, str(user["id"]))
        )
        scan = cursor.fetchone()
        cursor.close()
        conn.close()

        if not scan:
            raise HTTPException(status_code=404, detail="Scan results not found")

        return {
            'id': scan['id'],
            'cv_id': scan['cv_id'],
            'scan_date': scan['scan_date'],
            'total_issues': scan['total_issues'],
            'critical_count': scan['critical_count'],
            'high_count': scan['high_count'],
            'medium_count': scan['medium_count'],
            'low_count': scan['low_count'],
            'status': scan['status']
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{scan_id}")
async def get_detailed_report(scan_id: str, token: str):
    """Get full scan report with all issues (for report page)."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT * FROM cv_scan_results WHERE id = %s AND user_id = %s""",
            (scan_id, str(user["id"]))
        )
        scan = cursor.fetchone()
        cursor.close()
        conn.close()

        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")

        issues = scan.get('issues_json', [])
        if isinstance(issues, str):
            issues = json.loads(issues)

        cv_content_raw = scan.get('original_cv_content', '')
        # Strip structure markers for plain text output
        cv_content = strip_structure_markers(cv_content_raw) if cv_content_raw else ''
        # Convert markers to HTML for formatted display
        cv_content_html = convert_markers_to_html(cv_content_raw) if cv_content_raw else ''
        score_data = extract_cv_data_and_score(cv_content) if cv_content else calculate_cv_score_from_issues(issues)

        return {
            'scan_id': scan['id'],
            'scan_date': scan['scan_date'],
            'cv_content': cv_content,  # Clean text without markers
            'cv_content_html': cv_content_html,  # HTML-formatted with headings/bullets (fallback from markers)
            'html_content': scan.get('html_content'),  # Rich HTML from original document (may be None)
            'fixed_html_content': scan.get('fixed_html_content'),  # Rich HTML after fixes (may be None)
            'total_issues': scan['total_issues'],
            'critical_count': scan['critical_count'],
            'high_count': scan['high_count'],
            'medium_count': scan['medium_count'],
            'low_count': scan['low_count'],
            'issues': issues,
            'status': scan['status'],
            'cv_score': score_data['score'],
            'score_message': score_data['message'],
            'score_status': score_data['status'],
            'score_breakdown': score_data['breakdown'],
            'total_score': score_data['score'],
            'grade': score_data['status'],
            'breakdown': score_data['breakdown'],
            'score_version': score_data.get('version', '3.0.0')
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{scan_id}/summary")
async def get_report_summary(scan_id: str, token: str = ''):
    """Get summary data for Crossroads page."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT id, issues_json, original_cv_content, total_issues, 
                      critical_count, high_count, medium_count, low_count 
               FROM cv_scan_results WHERE id = %s AND user_id = %s""",
            (scan_id, str(user["id"]))
        )
        scan = cursor.fetchone()
        cursor.close()
        conn.close()

        if not scan:
            raise HTTPException(status_code=404, detail="Report not found")

        issues = scan.get('issues_json', [])
        if isinstance(issues, str):
            issues = json.loads(issues)

        # Use deterministic severity counting (supports legacy high/medium/low names)
        breakdown = count_issues_by_severity(issues)

        cv_content_raw = scan.get('original_cv_content', '')
        # Strip markers for clean scoring
        cv_content = strip_structure_markers(cv_content_raw) if cv_content_raw else ''
        score_data = extract_cv_data_and_score(cv_content) if cv_content else {'score': 0}

        return {
            'score': score_data.get('score', 0),
            'total_issues': len(issues),
            'breakdown': breakdown
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get summary")


CV_FIX_PROMPT = """
You are an expert CV writer. Your task is to SIGNIFICANTLY IMPROVE this CV by fixing all identified issues.

ORIGINAL CV:
---
{original_cv}
---

ISSUES TO FIX:
{issues_list}

═══════════════════════════════════════════════════════════
CRITICAL: ELEMENTS YOU MUST NEVER MODIFY
═══════════════════════════════════════════════════════════

DO NOT change the FORMAT of these elements. Preserve their exact structure:

1. EMAIL ADDRESSES
   - Keep format exactly: name@domain.com
   - DO NOT replace with: [Email] or "email address" or any placeholder
   - OK to fix typos: jonh@gmail.com → john@gmail.com

2. PHONE NUMBERS  
   - Keep format exactly: +1-555-123-4567 or (555) 123-4567
   - DO NOT replace with: [Phone] or "phone number" or any placeholder

3. LINKEDIN URLS
   - Keep format exactly: linkedin.com/in/username or full URL
   - DO NOT replace with: [LinkedIn Profile URL] or any placeholder
   - DO NOT remove the actual URL
   - If in markdown format [text](url), preserve both text and URL

4. GITHUB/PORTFOLIO URLS
   - Keep actual URLs intact, never replace with placeholders

EXAMPLES:
❌ WRONG: linkedin.com/in/johnsmith → [LinkedIn Profile URL]
✅ RIGHT: linkedin.com/in/johnsmith (keep exactly)

❌ WRONG: john.smith@gmail.com → [Email Address]  
✅ RIGHT: john.smith@gmail.com (keep exactly)

═══════════════════════════════════════════════════════════
TRANSFORMATION RULES (APPLY AGGRESSIVELY)
═══════════════════════════════════════════════════════════

1. QUANTIFICATION (Most Important)
   - Add numbers, percentages, dollar amounts to EVERY achievement
   - Use realistic estimates: "Managed team" → "Managed team of 8 engineers"
   - Add impact metrics: "Improved process" → "Improved process efficiency by 35%"
   - Include scale: "Handled projects" → "Delivered 12 projects worth $2.5M"

2. ACTION VERBS (Replace ALL weak verbs)
   - "Responsible for" → "Led", "Directed", "Managed"
   - "Worked on" → "Developed", "Built", "Created"
   - "Helped with" → "Contributed to", "Supported", "Enabled"
   - "Was involved in" → "Spearheaded", "Drove", "Executed"

3. PASSIVE TO ACTIVE VOICE
   - "The project was completed" → "Completed the project"
   - "Sales were increased" → "Increased sales by 40%"

4. VAGUE TO SPECIFIC
   - "Various tasks" → "Budget analysis, vendor negotiations, and quarterly reporting"
   - "Multiple projects" → "15 cross-functional projects"
   - "Large team" → "Team of 12 developers"

5. GRAMMAR AND SPELLING
   - Fix ALL errors
   - Ensure consistent tense (past for previous jobs)
   - Professional punctuation

═══════════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════════

Return ONLY the complete fixed CV text.
Do NOT include explanations, comments, or markdown formatting.
The output should be ready to use as a professional CV.

FIXED CV:
"""


# DEPRECATED: AI-based changes extraction replaced with code-based approach (Jan 2026)
# Cost savings: ~$0.005-0.01 per Auto-Fix call
# See: backend/common/detection/changes_extractor.py


@router.post("/fix/{scan_id}")
@limiter.limit("5/hour")
async def generate_fixed_cv(request: Request, scan_id: str, token: str):
    """Generate a fixed version of the CV."""
    logger.info(f"[CV_FIX] Starting fix for scan_id: {scan_id}")
    
    user = get_user_from_token(token)
    if not user:
        logger.error("[CV_FIX] Authentication failed - no user from token")
        raise HTTPException(status_code=401, detail="Not authenticated")

    logger.info(f"[CV_FIX] User authenticated: {user.get('email', 'unknown')}")

    try:
        conn = get_db_connection()
        if not conn:
            logger.error("[CV_FIX] Database connection failed")
            raise HTTPException(status_code=500, detail="Database not available")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT * FROM cv_scan_results WHERE id = %s AND user_id = %s""",
            (scan_id, str(user["id"]))
        )
        scan = cursor.fetchone()

        if not scan:
            cursor.close()
            conn.close()
            logger.error(f"[CV_FIX] Scan not found: {scan_id}")
            raise HTTPException(status_code=404, detail="Scan not found")

        logger.info(f"[CV_FIX] Scan found, status: {scan.get('status')}")

        if scan.get('fixed_cv_content'):
            cursor.close()
            conn.close()
            logger.info("[CV_FIX] Fixed CV already exists, returning cached")
            return {
                'success': True,
                'message': 'Fixed CV already generated',
                'scan_id': scan_id
            }

        original_content_raw = scan.get('original_cv_content', '')
        # Strip markers before sending to AI - markers are for detection only
        original_content = strip_structure_markers(original_content_raw) if original_content_raw else ''
        issues = scan.get('issues_json', [])
        if isinstance(issues, str):
            issues = json.loads(issues)

        logger.info(f"[CV_FIX] Original CV length: {len(original_content)} chars, Issues count: {len(issues)}")

        if not original_content:
            cursor.close()
            conn.close()
            logger.error("[CV_FIX] Original CV content is empty")
            raise HTTPException(status_code=400, detail="Original CV content not found")

        issues_text = "\n".join([
            f"- {issue.get('issue', '')} (Location: {issue.get('location', 'Unknown')}): {issue.get('suggested_fix', '')}"
            for issue in issues
        ])

        prompt = CV_FIX_PROMPT.format(
            original_cv=original_content,
            issues_list=issues_text
        )

        logger.info(f"[CV_FIX] Prompt length: {len(prompt)} chars (~{len(prompt)//4} tokens)")
        logger.info("[CV_FIX] Calling AI API (gemini) for CV fix...")

        try:
            ai_response = await generate_completion(
                prompt=prompt,
                user_id=str(user["id"]),
                service_name="cv_fix",
                provider="gemini",
                max_tokens=4000
            )
            fixed_content = ai_response.content if ai_response else ""
            logger.info(f"[CV_FIX] AI response received, length: {len(fixed_content)} chars, tokens: {ai_response.total_tokens if ai_response else 0}")
        except Exception as ai_error:
            logger.error(f"[CV_FIX] AI API ERROR: {type(ai_error).__name__}: {str(ai_error)}")
            cursor.close()
            conn.close()
            raise HTTPException(status_code=500, detail=f"AI generation failed: {str(ai_error)}")

        if not fixed_content:
            logger.error("[CV_FIX] AI returned empty response")
            cursor.close()
            conn.close()
            raise HTTPException(status_code=500, detail="AI returned empty response")

        # VALIDATION: Ensure AI didn't break critical elements (email, phone, LinkedIn)
        from backend.common.detection.fix_validator import validate_fix, restore_critical_elements
        
        is_valid, warnings = validate_fix(original_content, fixed_content)
        if not is_valid:
            for warning in warnings:
                logger.warning(f"[CV_FIX] {warning}")
            fixed_content = restore_critical_elements(original_content, fixed_content)
            logger.info("[CV_FIX] Critical elements restored after AI broke them")

        # Code-based changes extraction (no AI call - saves ~$0.005-0.01)
        # Replaced AI call on Jan 2026 for cost optimization
        logger.info("[CV_FIX] Extracting changes list (code-based)...")
        
        detected_issues = scan.get('issues_json', [])
        if isinstance(detected_issues, str):
            try:
                detected_issues = json.loads(detected_issues)
            except:
                detected_issues = []
        
        changes_data = extract_changes_code_based(
            original_cv=original_content,
            fixed_cv=fixed_content,
            detected_issues=detected_issues
        )
        logger.info(f"[CV_FIX] Extracted {len(changes_data.get('changes', []))} changes (code-based)")

        # STEP A: Get the ORIGINAL score (already calculated during scan)
        # DEBUG: Log content lengths and first/last 200 chars to verify they're different
        logger.info(f"[CV_FIX_DEBUG] Original content length: {len(original_content)} chars")
        logger.info(f"[CV_FIX_DEBUG] Fixed content length: {len(fixed_content)} chars")
        logger.info(f"[CV_FIX_DEBUG] Original first 200: {original_content[:200]}")
        logger.info(f"[CV_FIX_DEBUG] Fixed first 200: {fixed_content[:200]}")
        logger.info(f"[CV_FIX_DEBUG] Contents are identical: {original_content == fixed_content}")
        
        # DEBUG: Extract patterns separately to compare
        from backend.common.scoring.extractors.pattern_matcher_v31 import extract_patterns
        from backend.common.scoring.extractors.text_analyzer import analyze_text
        
        orig_patterns = extract_patterns(original_content)
        fixed_patterns = extract_patterns(fixed_content)
        orig_metrics = analyze_text(original_content)
        fixed_metrics = analyze_text(fixed_content)
        
        logger.info(f"[CV_FIX_DEBUG] Original patterns: {orig_patterns}")
        logger.info(f"[CV_FIX_DEBUG] Fixed patterns: {fixed_patterns}")
        logger.info(f"[CV_FIX_DEBUG] Original metrics: {orig_metrics}")
        logger.info(f"[CV_FIX_DEBUG] Fixed metrics: {fixed_metrics}")
        
        before_score_data = extract_cv_data_and_score(original_content)
        before_score = before_score_data['score']
        logger.info(f"[CV_FIX] Original CV score: {before_score}")

        # STEP B: Score the FIXED CV (NEW - actually calculate it!)
        fixed_score_data = extract_cv_data_and_score(fixed_content)
        after_score = fixed_score_data['score']
        logger.info(f"[CV_FIX] Fixed CV score: {after_score}")

        # STEP C: Calculate REAL improvement
        improvement = after_score - before_score
        logger.info(f"[CV_FIX] Real improvement: {improvement} points ({before_score} → {after_score})")

        cursor.execute(
            """UPDATE cv_scan_results 
               SET fixed_cv_content = %s, changes_json = %s, status = %s, updated_at = %s,
                   fixed_score = %s, improvement_percent = %s
               WHERE id = %s""",
            (fixed_content, json.dumps(changes_data), 'fixed', datetime.utcnow().isoformat(),
             after_score, improvement, scan_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"[CV_FIX] Successfully saved fixed CV with REAL scores for scan_id: {scan_id}")

        return {
            'success': True,
            'message': 'Fixed CV generated successfully',
            'scan_id': scan_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CV_FIX] UNEXPECTED ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"[CV_FIX] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fixed/{scan_id}")
async def get_fixed_cv(scan_id: str, token: str):
    """Get the fixed CV comparison data."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT * FROM cv_scan_results WHERE id = %s AND user_id = %s""",
            (scan_id, str(user["id"]))
        )
        scan = cursor.fetchone()
        cursor.close()
        conn.close()

        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")

        if not scan.get('fixed_cv_content'):
            raise HTTPException(status_code=400, detail="Fixed CV not generated yet")

        issues = scan.get('issues_json', [])
        if isinstance(issues, str):
            issues = json.loads(issues)

        # Get REAL scores from database (calculated during fix generation)
        original_content_raw = scan.get('original_cv_content', '')
        fixed_content = scan.get('fixed_cv_content', '')
        
        # Strip markers from original content for user display
        original_content = strip_structure_markers(original_content_raw) if original_content_raw else ''
        
        # Use stored scores if available, otherwise recalculate
        if scan.get('fixed_score') is not None:
            before_score_data = extract_cv_data_and_score(original_content)
            before_score = before_score_data['score']
            after_score = scan['fixed_score']
            improvement = scan.get('improvement_percent', after_score - before_score)
        else:
            # Fallback: recalculate both scores (for old records)
            before_score_data = extract_cv_data_and_score(original_content)
            after_score_data = extract_cv_data_and_score(fixed_content)
            before_score = before_score_data['score']
            after_score = after_score_data['score']
            improvement = after_score - before_score

        # Build category improvements from issues (for display only)
        category_improvements = calculate_after_fix_score(
            before_score=before_score,
            after_score=after_score,
            issues=issues
        )

        # Get changes data
        changes_json = scan.get('changes_json', {})
        if isinstance(changes_json, str):
            try:
                changes_json = json.loads(changes_json)
            except:
                changes_json = {}

        return {
            'scan_id': scan['id'],
            'original_cv_content': original_content,
            'fixed_cv_content': fixed_content,
            'total_issues': scan['total_issues'],
            'issues': issues,
            'status': scan['status'],
            'original_score': before_score,
            'fixed_score': after_score,
            'improvement': improvement,
            'category_improvements': category_improvements.get('category_improvements', {}),
            'before_score': before_score,
            'after_score': after_score,
            'score_version': '3.0.0',
            'changes': changes_json.get('changes', []),
            'changes_summary': changes_json.get('summary', {}),
            'total_changes': len(changes_json.get('changes', [])),
            'total_issues_fixed': category_improvements.get('total_issues_fixed', 0)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{scan_id}")
async def download_fixed_cv(scan_id: str, format: str = 'txt', token: str = ''):
    """Download the fixed CV in specified format."""
    logger.info(f"[CV_DOWNLOAD] Request - scan_id: {scan_id}, format: {format}")
    
    user = get_user_from_token(token)
    if not user:
        logger.error("[CV_DOWNLOAD] Authentication failed")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        conn = get_db_connection()
        if not conn:
            logger.error("[CV_DOWNLOAD] Database connection failed")
            raise HTTPException(status_code=500, detail="Database not available")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT fixed_cv_content FROM cv_scan_results WHERE id = %s AND user_id = %s""",
            (scan_id, str(user["id"]))
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result or not result.get('fixed_cv_content'):
            logger.error(f"[CV_DOWNLOAD] Fixed CV not found for scan_id: {scan_id}")
            raise HTTPException(status_code=404, detail="Fixed CV not found")

        content = result['fixed_cv_content']
        logger.info(f"[CV_DOWNLOAD] Content length: {len(content)} chars")

        if format == 'txt':
            logger.info("[CV_DOWNLOAD] Generating TXT file")
            return StreamingResponse(
                BytesIO(content.encode('utf-8')),
                media_type='text/plain',
                headers={'Content-Disposition': 'attachment; filename=fixed_cv.txt'}
            )

        elif format == 'pdf':
            logger.info("[CV_DOWNLOAD] Generating PDF file")
            try:
                pdf_bytes = generate_pdf(content)
                logger.info(f"[CV_DOWNLOAD] PDF generated, size: {len(pdf_bytes)} bytes")
            except Exception as pdf_error:
                logger.error(f"[CV_DOWNLOAD] PDF generation failed: {type(pdf_error).__name__}: {str(pdf_error)}")
                import traceback
                logger.error(f"[CV_DOWNLOAD] PDF traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(pdf_error)}")
            
            return StreamingResponse(
                BytesIO(pdf_bytes),
                media_type='application/pdf',
                headers={'Content-Disposition': 'attachment; filename=fixed_cv.pdf'}
            )

        elif format == 'docx':
            logger.info("[CV_DOWNLOAD] Generating DOCX file")
            try:
                docx_bytes = generate_docx(content)
                logger.info(f"[CV_DOWNLOAD] DOCX generated, size: {len(docx_bytes)} bytes")
            except Exception as docx_error:
                logger.error(f"[CV_DOWNLOAD] DOCX generation failed: {type(docx_error).__name__}: {str(docx_error)}")
                raise HTTPException(status_code=500, detail=f"DOCX generation failed: {str(docx_error)}")
            
            return StreamingResponse(
                BytesIO(docx_bytes),
                media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                headers={'Content-Disposition': 'attachment; filename=fixed_cv.docx'}
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use: txt, pdf, docx")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest")
async def get_latest_scan(token: str):
    """Get the most recent completed scan for current user."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT csr.id, csr.cv_id, csr.total_issues, csr.critical_count, 
                      csr.high_count, csr.medium_count, csr.low_count, 
                      csr.status, csr.created_at, csr.original_cv_content,
                      uc.filename as cv_filename
               FROM cv_scan_results csr
               LEFT JOIN user_cvs uc ON csr.cv_id::uuid = uc.id
               WHERE csr.user_id = %s 
                 AND csr.status = 'completed'
               ORDER BY csr.created_at DESC
               LIMIT 1""",
            (str(user["id"]),)
        )
        scan = cursor.fetchone()
        cursor.close()
        conn.close()

        if not scan:
            return None

        cv_content_raw = scan.get('original_cv_content', '')
        # Strip markers for clean scoring
        cv_content = strip_structure_markers(cv_content_raw) if cv_content_raw else ''
        score_data = extract_cv_data_and_score(cv_content) if cv_content else calculate_cv_score_from_issues([])
        
        created_at = scan.get("created_at")
        created_at_str = created_at.isoformat() if created_at else None

        return {
            "id": scan["id"],
            "cv_id": scan.get("cv_id"),
            "cv_filename": scan.get("cv_filename") or "Your CV",
            "score": score_data.get('score', 0),
            "total_issues": scan.get("total_issues", 0),
            "critical_count": scan.get("critical_count", 0),
            "high_count": scan.get("high_count", 0),
            "medium_count": scan.get("medium_count", 0),
            "low_count": scan.get("low_count", 0),
            "status": scan.get("status"),
            "created_at": created_at_str
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[GET_LATEST_SCAN] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scans/{scan_id}/archive")
async def archive_scan(scan_id: int, token: str):
    """Archive a scan (mark as not active, but keep for history)."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database not available")

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            """SELECT id FROM cv_scan_results WHERE id = %s AND user_id = %s""",
            (scan_id, str(user["id"]))
        )
        scan = cursor.fetchone()

        if not scan:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Scan not found")

        cursor.execute(
            """UPDATE cv_scan_results SET status = 'archived' WHERE id = %s""",
            (scan_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return {"success": True, "message": "Scan archived"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ARCHIVE_SCAN] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
