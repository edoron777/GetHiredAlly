import os
import json
import re
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from supabase import create_client, Client
from typing import Optional, Tuple, Dict, Any
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ai_service import generate_completion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analyze"])

def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return create_client(url, key)
    return None

class AnalyzeJobRequest(BaseModel):
    job_description: str = Field(..., min_length=10, max_length=50000)
    mode: str = Field(default='standard')
    interviewer_type: str = Field(default='general')
    provider: str = Field(default='claude')
    token: Optional[str] = Field(None, max_length=256)
    
    @field_validator('job_description')
    @classmethod
    def validate_job_description(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 10:
            raise ValueError('Job description must be at least 10 characters')
        return cleaned
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v: str) -> str:
        allowed = ['quick', 'standard', 'deep', 'max']
        if v.lower() not in allowed:
            raise ValueError(f'Mode must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @field_validator('interviewer_type')
    @classmethod
    def validate_interviewer_type(cls, v: str) -> str:
        allowed = ['hr', 'technical', 'manager', 'general']
        if v.lower() not in allowed:
            raise ValueError(f'Interviewer type must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        allowed = ['claude', 'gemini']
        if v.lower() not in allowed:
            raise ValueError(f'Provider must be one of: {", ".join(allowed)}')
        return v.lower()

class AnalyzeJobResponse(BaseModel):
    analysis: str
    mode: str

FALLBACK_SYSTEM_PROMPT = """You are an expert career coach and interview preparation specialist with 20+ years of experience helping candidates land their dream jobs. Your role is to provide detailed, actionable analysis that gives candidates a real competitive advantage.

Your analysis style is:
- Direct and practical, not generic
- Specific to the role and company
- Focused on what will actually help in the interview
- Honest about red flags or concerns

Always structure your response clearly with headers and bullet points for easy reading."""

FALLBACK_INTERVIEWER_PROMPTS = {
    "hr": """
INTERVIEWER FOCUS: HR / Recruiter Screen

Since this is an HR/Recruiter interview, emphasize:
- Cultural fit and soft skills they're looking for
- Salary expectations and benefits signals in the posting
- Work-life balance and company culture indicators
- Screening questions they're likely to ask
- How to present your career story compellingly
- Red flags in your background to address proactively""",
    
    "technical": """
INTERVIEWER FOCUS: Technical Interview

Since this is a Technical interview, emphasize:
- Specific technical skills and tools mentioned
- Experience levels required for each technology
- Types of technical problems they likely solve
- System design or architecture expectations
- Coding challenge topics to prepare
- Technical questions to ask about their stack""",
    
    "manager": """
INTERVIEWER FOCUS: Hiring Manager Interview

Since this is a Hiring Manager interview, emphasize:
- Team dynamics and collaboration style
- Deliverables and success metrics for the role
- Management style and autonomy level
- Growth opportunities and career path
- Challenges the team is facing
- How to demonstrate you'll make their life easier""",
    
    "general": """
INTERVIEWER FOCUS: General Preparation

Since you're not sure who will interview you, prepare for all angles:
- Technical skills and how you'll demonstrate them
- Behavioral questions and STAR format stories
- Cultural fit and soft skills
- Questions about your background and motivations
- Salary and benefits conversation preparation"""
}

JSON_STRUCTURE_SUFFIX = """

---

IMPORTANT: After your markdown report, you MUST include a structured JSON block.

Use this EXACT format:

---JSON_DATA_START---
{
  "company_name": "extracted company name or null",
  "job_title": "extracted job title",
  "seniority_level": "junior/mid/senior/lead/executive",
  "key_requirements": ["requirement 1", "requirement 2", "requirement 3"],
  "technical_skills": [
    {"skill": "skill name", "importance": "required/preferred/nice-to-have"}
  ],
  "soft_skills": [
    {"skill": "skill name", "evidence": "quote or signal from JD"}
  ],
  "red_flags": [
    {"flag": "description of concern", "severity": "low/medium/high"}
  ],
  "culture_signals": ["signal 1", "signal 2"],
  "interview_topics": ["topic 1", "topic 2", "topic 3"],
  "questions_to_ask": ["question 1", "question 2"]
}
---JSON_DATA_END---
"""

FALLBACK_DEPTH_PROMPTS = {
    "ready": """
OUTPUT FORMAT: Interview Ready (Concise)

Provide a FOCUSED analysis covering the essentials:
- 5-7 key requirements to highlight
- 3-4 likely interview questions with answer frameworks
- Top 3 things that will make you stand out
- 2-3 smart questions to ask them

Keep your response between 600-900 words. Be direct and actionable.""" + JSON_STRUCTURE_SUFFIX,

    "full": """
OUTPUT FORMAT: Fully Prepared (Comprehensive)

Provide a THOROUGH analysis covering everything:

1. **Role Overview** - What this role really involves
2. **Must-Have Skills** - Non-negotiable requirements
3. **Nice-to-Have Skills** - Differentiators to highlight
4. **Hidden Expectations** - Reading between the lines
5. **Company Culture Signals** - What the language tells us
6. **Red Flags & Concerns** - Things to clarify
7. **Interview Questions** - 8-10 likely questions with answer guidance
8. **Your Talking Points** - Key themes to weave into answers
9. **Questions to Ask Them** - Smart questions that impress
10. **Preparation Checklist** - Specific things to do before the interview

Provide 1500-2000 words of detailed, actionable guidance.""" + JSON_STRUCTURE_SUFFIX
}

def parse_analysis_response(response_text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Splits Claude's response into markdown report and structured JSON.
    Returns: (markdown_text, structured_data_dict)
    """
    if "---JSON_DATA_START---" in response_text:
        parts = response_text.split("---JSON_DATA_START---")
        markdown = parts[0].strip()
        try:
            json_str = parts[1].split("---JSON_DATA_END---")[0].strip()
            structured_data = json.loads(json_str)
            logger.info("Successfully parsed structured JSON from response")
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Failed to parse JSON from response: {e}")
            structured_data = None
    else:
        markdown = response_text
        structured_data = None
        logger.info("No JSON structure found in response")
    
    return markdown, structured_data

async def save_analysis_to_db(
    user_id: Optional[str],
    job_description: str,
    depth_level: str,
    interviewer_type: str,
    markdown: str,
    structured_data: Optional[Dict[str, Any]]
) -> Optional[str]:
    """Save the analysis to the database. Returns the analysis ID if successful."""
    supabase = get_supabase_client()
    if not supabase:
        logger.warning("Supabase not available, skipping database save")
        return None
    
    try:
        jd_result = supabase.table('job_descriptions').insert({
            'user_id': user_id,
            'raw_text': job_description
        }).execute()
        
        if not jd_result.data:
            logger.error("Failed to insert job description")
            return None
        
        jd_id = jd_result.data[0]['id']
        
        analysis_result = supabase.table('xray_analyses').insert({
            'job_description_id': jd_id,
            'user_id': user_id,
            'depth_level': depth_level,
            'interviewer_type': interviewer_type,
            'report_markdown': markdown,
            'structured_output': structured_data
        }).execute()
        
        if analysis_result.data:
            logger.info(f"Saved analysis to database with ID: {analysis_result.data[0]['id']}")
            return analysis_result.data[0]['id']
        
    except Exception as e:
        logger.error(f"Failed to save analysis to database: {e}")
    
    return None

async def get_combined_prompt(interviewer_type: str, depth_level: str) -> str:
    supabase = get_supabase_client()
    
    system_prompt = ""
    interviewer_prompt = ""
    depth_prompt = ""
    
    logger.info(f"Fetching prompts for interviewer_type={interviewer_type}, depth_level={depth_level}")
    
    if supabase:
        logger.info("Supabase client connected")
        
        try:
            logger.info("Querying: service_name='xray_analyzer', template_type='system_v2'")
            system_result = supabase.table('prompt_templates').select('content').eq('service_name', 'xray_analyzer').eq('template_type', 'system_v2').limit(1).execute()
            if system_result.data and len(system_result.data) > 0 and system_result.data[0].get('content'):
                system_prompt = system_result.data[0]['content']
                logger.info(f"Found system_v2 prompt: {len(system_prompt)} chars")
            else:
                logger.warning("No system_v2 prompt found in database")
        except Exception as e:
            logger.error(f"Error fetching system_v2: {e}")
        
        try:
            interviewer_template = f'interviewer_{interviewer_type}'
            logger.info(f"Querying: service_name='xray_analyzer', template_type='{interviewer_template}'")
            interviewer_result = supabase.table('prompt_templates').select('content').eq('service_name', 'xray_analyzer').eq('template_type', interviewer_template).limit(1).execute()
            if interviewer_result.data and len(interviewer_result.data) > 0 and interviewer_result.data[0].get('content'):
                interviewer_prompt = interviewer_result.data[0]['content']
                logger.info(f"Found {interviewer_template} prompt: {len(interviewer_prompt)} chars")
            else:
                logger.warning(f"No {interviewer_template} prompt found in database")
        except Exception as e:
            logger.error(f"Error fetching interviewer prompt: {e}")
        
        try:
            depth_template = f'depth_{depth_level}'
            logger.info(f"Querying: service_name='xray_analyzer', template_type='{depth_template}'")
            depth_result = supabase.table('prompt_templates').select('content').eq('service_name', 'xray_analyzer').eq('template_type', depth_template).limit(1).execute()
            if depth_result.data and len(depth_result.data) > 0 and depth_result.data[0].get('content'):
                depth_prompt = depth_result.data[0]['content']
                logger.info(f"Found {depth_template} prompt: {len(depth_prompt)} chars")
            else:
                logger.warning(f"No {depth_template} prompt found in database")
        except Exception as e:
            logger.error(f"Error fetching depth prompt: {e}")
    else:
        logger.warning("Supabase client not available - using fallbacks")
    
    if not system_prompt:
        logger.info("Using FALLBACK system prompt")
        system_prompt = FALLBACK_SYSTEM_PROMPT
    if not interviewer_prompt:
        logger.info(f"Using FALLBACK interviewer prompt for {interviewer_type}")
        interviewer_prompt = FALLBACK_INTERVIEWER_PROMPTS.get(interviewer_type, FALLBACK_INTERVIEWER_PROMPTS["general"])
    if not depth_prompt:
        logger.info(f"Using FALLBACK depth prompt for {depth_level}")
        depth_prompt = FALLBACK_DEPTH_PROMPTS.get(depth_level, FALLBACK_DEPTH_PROMPTS["full"])
    
    if JSON_STRUCTURE_SUFFIX not in depth_prompt:
        depth_prompt = depth_prompt + JSON_STRUCTURE_SUFFIX
        logger.info("Appended JSON_STRUCTURE_SUFFIX to depth prompt")
    
    combined = f"{system_prompt}\n\n{interviewer_prompt}\n\n{depth_prompt}"
    logger.info(f"Combined prompt length: {len(combined)} chars")
    
    return combined

@router.get("/xray/analyses")
async def list_xray_analyses(token: str):
    """List user's X-Ray analyses for Smart Questions selection"""
    import hashlib
    
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    session_result = supabase.table("user_sessions").select("user_id").eq("token_hash", token_hash).execute()
    
    if not session_result.data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    user_id = session_result.data[0]["user_id"]
    
    try:
        result = supabase.table("xray_analyses").select(
            "id, job_title, company_name, created_at"
        ).eq("user_id", user_id).order("created_at", desc=True).limit(20).execute()
        
        return {"analyses": result.data or []}
    except Exception as e:
        logger.error(f"Error fetching analyses: {e}")
        return {"analyses": []}

@router.post("/analyze-job", response_model=AnalyzeJobResponse)
async def analyze_job(request: AnalyzeJobRequest):
    if len(request.job_description) < 100:
        raise HTTPException(status_code=400, detail="Job description must be at least 100 characters")
    
    depth_level = "ready" if request.mode == "quick" else "full"
    interviewer_type = request.interviewer_type if request.interviewer_type in ["hr", "technical", "manager", "general"] else "general"
    
    try:
        system_prompt = await get_combined_prompt(interviewer_type, depth_level)
        
        max_tokens = 2500 if depth_level == "ready" else 5000
        
        provider = request.provider if request.provider in ['claude', 'gemini'] else 'claude'
        
        ai_response = await generate_completion(
            prompt=f"Analyze this job description:\n\n{request.job_description}",
            system_prompt=system_prompt,
            provider=provider,
            max_tokens=max_tokens,
            temperature=0.7,
            user_id=None,
            service_name="xray"
        )
        
        analysis_text = ai_response.content or "Unable to generate analysis"
        
        markdown, structured_data = parse_analysis_response(analysis_text)
        
        await save_analysis_to_db(
            user_id=None,
            job_description=request.job_description,
            depth_level=depth_level,
            interviewer_type=interviewer_type,
            markdown=markdown,
            structured_data=structured_data
        )
        
        return AnalyzeJobResponse(
            analysis=markdown,
            mode=request.mode
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
