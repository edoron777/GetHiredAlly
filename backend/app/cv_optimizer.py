"""CV Optimizer scanning and analysis endpoints."""
import os
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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cv-optimizer", tags=["cv-optimizer"])


def get_db_connection():
    """Get direct PostgreSQL connection."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return None
    return psycopg2.connect(database_url)


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
- severity: "critical" | "high" | "medium" | "low"
- category: one of the categories below
- location: where in the CV (section name)
- current_text: the exact problematic text (quote it)
- suggested_fix: how to fix it with example
- fix_difficulty: "quick" | "medium" | "complex"

SEVERITY GUIDE:
- critical: Will cause immediate rejection (spelling errors, missing contact info)
- high: Major competitive disadvantage (passive language, no metrics, unexplained gaps)
- medium: Optimization opportunity (formatting issues, weak summary, outdated skills)
- low: Minor polish (small improvements, nice-to-haves)

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
  {{"id": 1, "issue": "Spelling error", "severity": "critical", "category": "Spelling & Grammar", "location": "Professional Summary", "current_text": "Developped", "suggested_fix": "Developed", "fix_difficulty": "quick"}},
  {{"id": 2, "issue": "Missing email", "severity": "critical", "category": "Missing Information", "location": "Contact Section", "current_text": "Phone only listed", "suggested_fix": "Add professional email like firstname.lastname@email.com", "fix_difficulty": "quick"}}
]
"""


def parse_ai_json_response(response_text: str) -> list:
    """Robust JSON parsing that handles markdown code fences and extra text."""
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
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON array in the text
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end > start:
        json_text = text[start:end + 1]
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            # JSON might be truncated - try to fix it
            json_text = fix_truncated_json(json_text)
            return json.loads(json_text)
    
    raise json.JSONDecodeError("No valid JSON array found", text, 0)


def fix_truncated_json(json_text: str) -> str:
    """Attempt to fix truncated JSON array by closing open structures."""
    text = json_text.rstrip()
    
    # Count open braces/brackets
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')
    
    # If we're inside an incomplete object, try to close it gracefully
    if open_braces > 0 or open_brackets > 0:
        # Find the last complete object
        last_complete = text.rfind('},')
        if last_complete != -1:
            text = text[:last_complete + 1]
        else:
            # Try to find last complete object without comma
            last_complete = text.rfind('}')
            if last_complete != -1 and last_complete > text.rfind('{'):
                text = text[:last_complete + 1]
        
        # Close the array
        if not text.endswith(']'):
            text = text.rstrip(',') + ']'
    
    return text


async def analyze_cv_with_ai(cv_content: str, user_id: str) -> dict:
    prompt = CV_ANALYSIS_PROMPT.format(cv_content=cv_content)

    try:
        ai_response = await generate_completion(
            prompt=prompt,
            provider='gemini',
            max_tokens=8192,
            temperature=0.3,
            user_id=user_id,
            service_name="cv_optimizer"
        )

        logger.info(f"[CV_SCAN] Raw AI response length: {len(ai_response.content)} chars")
        logger.info(f"[CV_SCAN] Raw AI response first 500 chars: {ai_response.content[:500]}")
        logger.info(f"[CV_SCAN] Raw AI response last 500 chars: {ai_response.content[-500:]}")

        issues = parse_ai_json_response(ai_response.content)
        
        logger.info(f"[CV_SCAN] Successfully parsed {len(issues)} issues")

        return {
            'issues': issues,
            'raw_response': ai_response.content
        }

    except json.JSONDecodeError as e:
        logger.error(f"[CV_SCAN] JSON parsing failed: {str(e)}")
        logger.error(f"[CV_SCAN] Full AI response for debugging:\n{ai_response.content}")
        return {
            'issues': [{
                'id': 1,
                'issue': 'Analysis parsing error',
                'severity': 'high',
                'category': 'System',
                'location': 'N/A',
                'current_text': 'Could not parse CV properly',
                'suggested_fix': 'Please try again or contact support',
                'fix_difficulty': 'complex'
            }],
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"[CV_SCAN] AI analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


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

        analysis_result = await analyze_cv_with_ai(cv_content, str(user["id"]))

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

        return {
            'scan_id': scan_id,
            'summary': summary,
            'issues': issues
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

        return {
            'scan_id': scan['id'],
            'scan_date': scan['scan_date'],
            'cv_content': scan.get('original_cv_content', ''),
            'total_issues': scan['total_issues'],
            'critical_count': scan['critical_count'],
            'high_count': scan['high_count'],
            'medium_count': scan['medium_count'],
            'low_count': scan['low_count'],
            'issues': issues,
            'status': scan['status']
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


CV_FIX_PROMPT = """You are a CV/Resume expert. Your task is to fix this CV based on the issues identified.

ORIGINAL CV:
---
{original_cv}
---

ISSUES TO FIX:
{issues_list}

INSTRUCTIONS:
1. Fix ALL the issues listed above
2. Maintain the original structure and format of the CV
3. Keep the same sections and order
4. Only change what needs to be fixed
5. Improve weak language to strong action verbs
6. Add quantification where possible (use realistic estimates if needed)
7. Fix all spelling and grammar errors
8. Ensure professional tone throughout

OUTPUT:
Return the complete fixed CV. Do NOT include any explanations or comments.
Just output the corrected CV text, ready to be used.

FIXED CV:
"""


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

        original_content = scan.get('original_cv_content', '')
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

        cursor.execute(
            """UPDATE cv_scan_results SET fixed_cv_content = %s, status = %s, updated_at = %s WHERE id = %s""",
            (fixed_content, 'fixed', datetime.utcnow().isoformat(), scan_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"[CV_FIX] Successfully saved fixed CV for scan_id: {scan_id}")

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

        return {
            'scan_id': scan['id'],
            'original_cv_content': scan.get('original_cv_content', ''),
            'fixed_cv_content': scan['fixed_cv_content'],
            'total_issues': scan['total_issues'],
            'issues': issues,
            'status': scan['status']
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
