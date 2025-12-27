import os
import json
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Any
import google.generativeai as genai
from supabase import create_client, Client

router = APIRouter(prefix="/api/smart-questions", tags=["smart-questions"])

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    return create_client(url, key)

def get_gemini_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-pro-preview-05-06')

class GenerateRequest(BaseModel):
    xray_analysis_id: Optional[str] = None
    job_description: Optional[str] = None
    cv_text: Optional[str] = None
    token: str

class EligibilityResponse(BaseModel):
    eligible: bool
    reason: str
    free_trial_used: bool

def build_smart_questions_prompt(job_data: str, cv_text: Optional[str] = None) -> str:
    cv_section = ""
    if cv_text:
        cv_section = f"""
## CANDIDATE'S CV/RESUME:
{cv_text}

Analyze the CV against the job requirements to identify:
- Skills gaps or missing experience
- Areas where the candidate may be challenged
- Strengths that should be highlighted
"""
    
    prompt = f"""You are an expert interview preparation coach. Your task is to generate personalized interview questions based on a job description and optionally a candidate's CV.

## JOB INFORMATION:
{job_data}
{cv_section}

## YOUR TASK:
Generate a comprehensive set of personalized interview questions that this specific candidate is likely to face.

## OUTPUT FORMAT (JSON):
Return a JSON object with this exact structure:
{{
    "weak_areas": [
        {{
            "area": "Leadership Experience",
            "risk_level": "high",
            "detection_reason": "CV shows individual contributor roles only, but job requires team management",
            "preparation_tip": "Prepare examples of informal leadership, mentoring, or project coordination"
        }}
    ],
    "questions": [
        {{
            "category": "behavioral",
            "question_text": "Tell me about a time you led a project from start to finish",
            "personalized_context": "Based on your background as an individual contributor, they'll probe your leadership abilities",
            "why_they_ask": "Testing your leadership potential and ability to manage complexity",
            "good_answer_example": "Use STAR method: Describe a project where you took initiative, coordinated with others, and delivered results",
            "what_to_avoid": "Don't say you've never led anything - even informal leadership counts",
            "source": "cv_gap"
        }}
    ]
}}

## QUESTION CATEGORIES:
- universal: Basic questions asked in every interview
- behavioral: Past experience questions (STAR method)
- situational: Hypothetical scenario questions
- self_assessment: Questions about strengths/weaknesses
- cultural_fit: Questions about work style and values
- technical: Role-specific technical questions

## QUESTION SOURCES:
- job_specific: Derived from specific job requirements
- cv_gap: Addressing gaps between CV and job requirements
- industry_standard: Common questions for this type of role
- company_culture: Based on company values mentioned

## GUIDELINES:
1. Generate 10-15 personalized questions
2. Include at least 2 questions for each identified weak area
3. Make questions specific to the role and candidate
4. Provide actionable preparation tips
5. If no CV provided, focus on job-specific questions
6. Include a mix of behavioral and situational questions

Return ONLY valid JSON, no markdown formatting or additional text."""

    return prompt

def parse_gemini_response(response_text: str) -> dict:
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}")

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
async def generate_smart_questions(request: GenerateRequest):
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
    
    model = get_gemini_model()
    prompt = build_smart_questions_prompt(xray_data, request.cv_text)
    
    try:
        response = model.generate_content(prompt)
        result = parse_gemini_response(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
    
    input_tokens = None
    output_tokens = None
    if hasattr(response, 'usage_metadata'):
        input_tokens = getattr(response.usage_metadata, 'prompt_token_count', None)
        output_tokens = getattr(response.usage_metadata, 'candidates_token_count', None)
    
    record = {
        "user_id": user_id,
        "xray_analysis_id": request.xray_analysis_id,
        "job_title": job_title,
        "company_name": company_name,
        "cv_provided": bool(request.cv_text),
        "weak_areas": result.get("weak_areas", []),
        "personalized_questions": result.get("questions", []),
        "generation_model": "gemini-2.5-pro",
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
        "weak_areas": result.get("weak_areas", []),
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
