import os
import json
import sys
import uuid
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from supabase import create_client, Client

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ai_service import generate_completion
from config.rate_limiter import limiter
from utils.encryption import encrypt_text, decrypt_text

router = APIRouter(prefix="/api/smart-questions", tags=["smart-questions"])

def validate_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError):
        return False

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    return create_client(url, key)


class GenerateRequest(BaseModel):
    xray_analysis_id: Optional[str] = Field(None, max_length=256)
    job_description: Optional[str] = Field(None, max_length=50000)
    cv_text: Optional[str] = Field(None, max_length=100000)
    token: str = Field(..., min_length=1, max_length=256)
    provider: Optional[str] = Field(default='gemini')
    
    @field_validator('xray_analysis_id')
    @classmethod
    def validate_xray_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            if not validate_uuid(v):
                raise ValueError('Invalid analysis ID format')
        return v
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: Optional[str]) -> str:
        if v is None:
            return 'gemini'
        allowed = ['claude', 'gemini']
        if v.lower() not in allowed:
            raise ValueError(f'Provider must be one of: {", ".join(allowed)}')
        return v.lower()

class EligibilityResponse(BaseModel):
    eligible: bool
    reason: str
    free_trial_used: bool

def build_smart_questions_prompt(job_data: str, cv_text: Optional[str] = None) -> str:
    prompt = """CRITICAL: You must respond with ONLY valid JSON. No text before or after. No markdown. No code blocks.

You are an INTELLIGENT HUMAN INTERVIEWER who has carefully studied both the job description AND the candidate's background. Your task is to prepare PERSONALIZED interview questions that a smart interviewer would ask THIS specific candidate.

Think like an interviewer who has done their homework and wants to ask questions that:
- Reference SPECIFIC details from the candidate's CV/background
- Connect to SPECIFIC requirements from the job description
- Sound like a real interviewer who knows the candidate's story

JOB DESCRIPTION:
"""
    prompt += job_data[:4000]
    
    if cv_text:
        prompt += """

CANDIDATE'S CV/BACKGROUND:
"""
        prompt += cv_text[:2000]
        prompt += """

IMPORTANT: Since you have the candidate's CV, you MUST personalize questions by:
- Referencing their specific companies, roles, or achievements
- Asking about gaps or transitions in their career
- Connecting their past experience to the new role's requirements

Example transformation:
- Generic: "Tell me about yourself"
- Personalized: "I see you spent 2 years at [Company]. Walk me through how that experience prepared you for this [Role] position."
"""
    
    prompt += """

Generate a JSON response with this EXACT structure:

{"focus_areas":[{"area":"string","priority_level":"KEY_FOCUS|WORTH_PREPARING|GOOD_TO_KNOW","focus_reason":"string","coaching_tip":"string","winning_approach":"string"}],"questions":[{"category":"universal|behavioral|situational|self_assessment|cultural_fit","question_text":"string","why_they_ask":"string","good_answer_example":"string","what_to_avoid":"string"}]}

RULES:
1. Generate 3-4 focus_areas (areas where preparation will help the candidate shine)
   - Compare JD requirements vs CV experience to identify preparation opportunities
   - Use positive, coaching language - these are OPPORTUNITIES, not weaknesses
   - priority_level: KEY_FOCUS (important gaps), WORTH_PREPARING (helpful), GOOD_TO_KNOW (nice to have)
   - coaching_tip: Brief, encouraging advice
   - winning_approach: How to turn this into a strength with a specific strategy

2. Generate exactly 15-18 PERSONALIZED questions with this mix:
   - 3-4 Universal questions (personalized to their background)
   - 5-6 Behavioral questions (referencing their specific experiences)
   - 3-4 Situational questions (based on role requirements)
   - 2-3 Self-Assessment questions
   - 2-3 Cultural Fit questions

3. PERSONALIZATION IS KEY:
   - Each question should feel like it was written for THIS candidate
   - Reference specific companies, roles, achievements, or gaps from their CV
   - Connect questions to specific job requirements
   - Example: Instead of "Tell me about a leadership challenge" → "Tell me about a leadership challenge you faced when managing the 5-person team at [Company]"

4. Keep answer examples brief (2-3 sentences max)
5. Keep what_to_avoid brief (1-2 sentences max)
6. Frame ALL language positively and supportively

Your ENTIRE response must be valid JSON starting with { and ending with }. Nothing else."""
    
    return prompt

def parse_gemini_response(response_text: str) -> dict:
    """Parse AI response with error recovery for truncated JSON"""
    text = response_text.strip()
    
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        text = text[start_idx:end_idx + 1]
    
    try:
        result = json.loads(text)
        return validate_smart_questions_response(result)
    except json.JSONDecodeError as e:
        print(f"Initial JSON parse failed: {e}, attempting recovery...")
        
        for i in range(len(text), 0, -50):
            try:
                test_text = text[:i]
                
                open_quotes = test_text.count('"') % 2
                if open_quotes:
                    test_text += '"'
                
                open_brackets = test_text.count('[') - test_text.count(']')
                open_braces = test_text.count('{') - test_text.count('}')
                
                test_text += ']' * max(0, open_brackets)
                test_text += '}' * max(0, open_braces)
                
                result = json.loads(test_text)
                print(f"Recovered JSON by truncating at position {i}")
                return validate_smart_questions_response(result)
            except:
                continue
        
        print(f"JSON recovery failed, returning empty structure")
        return {
            "focus_areas": [],
            "questions": [],
            "parse_error": str(e)
        }

def validate_smart_questions_response(data: dict) -> dict:
    """Ensure response has required structure"""
    if "focus_areas" not in data:
        data["focus_areas"] = []
    
    if "questions" not in data:
        data["questions"] = []
    
    valid_questions = []
    for q in data["questions"]:
        if isinstance(q, dict) and q.get("question_text"):
            if "category" not in q:
                q["category"] = "universal"
            if "why_they_ask" not in q:
                q["why_they_ask"] = ""
            if "good_answer_example" not in q:
                q["good_answer_example"] = ""
            if "what_to_avoid" not in q:
                q["what_to_avoid"] = ""
            valid_questions.append(q)
    
    data["questions"] = valid_questions
    return data

async def get_user_from_token(token: str) -> dict:
    import hashlib
    supabase = get_supabase_client()
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    session_result = supabase.table("user_sessions").select("*").eq("token_hash", token_hash).execute()
    
    if not session_result.data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    session = session_result.data[0]
    user_id = session["user_id"]
    
    user_result = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_result.data[0]

@router.get("/check-eligibility")
async def check_eligibility(token: str = Query(...)):
    """Check if user can use Smart Questions (free trial or paid)"""
    user = await get_user_from_token(token)
    
    free_used = user.get("smart_questions_free_used", False)
    is_paid = False
    
    if is_paid:
        return {"eligible": True, "reason": "paid_user", "free_trial_used": free_used}
    elif not free_used:
        return {"eligible": True, "reason": "free_trial", "free_trial_used": False}
    else:
        return {"eligible": False, "reason": "free_trial_exhausted", "free_trial_used": True}

@router.post("/generate")
@limiter.limit("10/hour")
async def generate_smart_questions(http_request: Request, request: GenerateRequest):
    """Generate personalized interview questions using Gemini"""
    
    user = await get_user_from_token(request.token)
    user_id = str(user["id"])
    
    free_used = user.get("smart_questions_free_used", False)
    is_paid = False
    
    if not is_paid and free_used:
        raise HTTPException(status_code=403, detail="Free trial exhausted. Please upgrade to continue.")
    
    eligibility_reason = "paid_user" if is_paid else "free_trial"
    
    supabase = get_supabase_client()
    
    xray_data = None
    job_title = "Unknown Position"
    company_name = None
    
    if request.xray_analysis_id:
        try:
            xray_result = supabase.table("xray_analyses").select("*").eq("id", request.xray_analysis_id).execute()
            if xray_result.data:
                xray_analysis = xray_result.data[0]
                xray_data = xray_analysis.get("structured_output") or xray_analysis.get("report_markdown")
                if isinstance(xray_data, dict):
                    xray_data = json.dumps(xray_data)
        except Exception:
            pass
    
    if not xray_data and request.job_description:
        xray_data = request.job_description
        lines = request.job_description.strip().split('\n')
        if lines and len(lines[0]) < 100:
            job_title = lines[0].strip()
    
    if not xray_data:
        raise HTTPException(status_code=400, detail="Either xray_analysis_id or job_description is required")
    
    prompt = build_smart_questions_prompt(xray_data, request.cv_text)
    
    provider = request.provider if request.provider in ['claude', 'gemini'] else 'gemini'
    
    try:
        ai_response = await generate_completion(
            prompt=prompt,
            provider=provider,
            max_tokens=8192,
            temperature=0.7,
            user_id=user_id,
            service_name="smart_questions"
        )
        result = parse_gemini_response(ai_response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
    
    input_tokens = ai_response.input_tokens
    output_tokens = ai_response.output_tokens
    
    encrypted_cv = encrypt_text(request.cv_text) if request.cv_text else None
    
    record = {
        "user_id": user_id,
        "xray_analysis_id": request.xray_analysis_id,
        "job_title": job_title,
        "company_name": company_name,
        "cv_provided": bool(request.cv_text),
        "cv_text_encrypted": encrypted_cv,
        "focus_areas": result.get("focus_areas", []),
        "personalized_questions": result.get("questions", []),
        "generation_model": "gemini-2.0-flash",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens
    }
    
    try:
        save_result = supabase.table("smart_question_results").insert(record).execute()
        saved_id = save_result.data[0]["id"] if save_result.data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save results: {str(e)}")
    
    if eligibility_reason == "free_trial":
        try:
            supabase.table("users").update({"smart_questions_free_used": True}).eq("id", user_id).execute()
        except Exception:
            pass
    
    return {
        "id": saved_id,
        "job_title": job_title,
        "company_name": company_name,
        "focus_areas": result.get("focus_areas", []),
        "questions": result.get("questions", []),
        "questions_count": len(result.get("questions", [])),
        "message": "Smart questions generated successfully"
    }

@router.get("/{result_id}")
async def get_smart_questions_result(result_id: str, token: str = Query(...)):
    """Get a specific smart questions result"""
    user = await get_user_from_token(token)
    user_id = str(user["id"])
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("smart_question_results").select("*").eq("id", result_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Result not found")
        
        record = result.data[0]
        
        if str(record["user_id"]) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/")
async def list_smart_questions(token: str = Query(...), limit: int = Query(default=10, le=50)):
    """List user's smart question results"""
    user = await get_user_from_token(token)
    user_id = str(user["id"])
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("smart_question_results").select("id, job_title, company_name, created_at, cv_provided").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        
        return {"results": result.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
