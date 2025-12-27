"""CV Optimizer scanning and analysis endpoints."""
import os
import sys
import json
import hashlib
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from supabase import create_client, Client

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ai_service import generate_completion
from utils.encryption import decrypt_text
from config.rate_limiter import limiter

router = APIRouter(prefix="/api/cv-optimizer", tags=["cv-optimizer"])


def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def get_user_from_token(token: str) -> dict | None:
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
- critical: Will cause immediate rejection (spelling errors, missing contact info, unprofessional email)
- high: Major competitive disadvantage (passive language, no metrics, unexplained gaps)
- medium: Optimization opportunity (formatting issues, weak summary, outdated skills)
- low: Minor polish (small improvements, nice-to-haves)

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


async def analyze_cv_with_ai(cv_content: str, user_id: str) -> dict:
    prompt = CV_ANALYSIS_PROMPT.format(cv_content=cv_content)

    try:
        ai_response = await generate_completion(
            prompt=prompt,
            provider='gemini',
            max_tokens=4096,
            temperature=0.3,
            user_id=user_id,
            service_name="cv_optimizer"
        )

        response_text = ai_response.content.strip()

        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        issues = json.loads(response_text)

        return {
            'issues': issues,
            'raw_response': ai_response.content
        }

    except json.JSONDecodeError as e:
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

    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        cv_result = client.table("user_cvs").select("*").eq("id", scan_request.cv_id).eq("user_id", user["id"]).execute()

        if not cv_result.data:
            raise HTTPException(status_code=404, detail="CV not found")

        cv = cv_result.data[0]
        cv_content = cv.get("content", "")

        if cv_content:
            try:
                cv_content = decrypt_text(cv_content)
            except Exception:
                pass

        if not cv_content or len(cv_content.strip()) < 50:
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

        scan_record = {
            'user_id': str(user["id"]),
            'cv_id': scan_request.cv_id,
            'total_issues': summary['total'],
            'critical_count': summary['critical'],
            'high_count': summary['high'],
            'medium_count': summary['medium'],
            'low_count': summary['low'],
            'original_cv_content': cv_content,
            'issues_json': issues,
            'status': 'completed'
        }

        save_result = client.table("cv_scan_results").insert(scan_record).execute()

        if not save_result.data:
            raise HTTPException(status_code=500, detail="Failed to save scan results")

        scan_id = save_result.data[0]["id"]

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

    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        result = client.table("cv_scan_results").select(
            "id, user_id, cv_id, scan_date, total_issues, critical_count, high_count, medium_count, low_count, status"
        ).eq("id", scan_id).eq("user_id", user["id"]).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Scan results not found")

        scan = result.data[0]

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

    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        result = client.table("cv_scan_results").select("*").eq("id", scan_id).eq("user_id", user["id"]).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Scan not found")

        scan = result.data[0]

        issues = scan.get('issues_json', [])
        if isinstance(issues, str):
            issues = json.loads(issues)

        return {
            'scan_id': scan['id'],
            'scan_date': scan['scan_date'],
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
