import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analyze"])

AI_INTEGRATIONS_ANTHROPIC_API_KEY = os.environ.get("AI_INTEGRATIONS_ANTHROPIC_API_KEY")
AI_INTEGRATIONS_ANTHROPIC_BASE_URL = os.environ.get("AI_INTEGRATIONS_ANTHROPIC_BASE_URL")

anthropic_client = Anthropic(
    api_key=AI_INTEGRATIONS_ANTHROPIC_API_KEY,
    base_url=AI_INTEGRATIONS_ANTHROPIC_BASE_URL
)

def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return create_client(url, key)
    return None

class AnalyzeJobRequest(BaseModel):
    job_description: str
    mode: str
    interviewer_type: str

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

FALLBACK_DEPTH_PROMPTS = {
    "ready": """
OUTPUT FORMAT: Interview Ready (Concise)

Provide a FOCUSED analysis covering the essentials:
- 5-7 key requirements to highlight
- 3-4 likely interview questions with answer frameworks
- Top 3 things that will make you stand out
- 2-3 smart questions to ask them

Keep your response between 600-900 words. Be direct and actionable.""",

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

Provide 1500-2000 words of detailed, actionable guidance."""
}

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
    
    combined = f"{system_prompt}\n\n{interviewer_prompt}\n\n{depth_prompt}"
    logger.info(f"Combined prompt length: {len(combined)} chars")
    
    return combined

@router.post("/analyze-job", response_model=AnalyzeJobResponse)
async def analyze_job(request: AnalyzeJobRequest):
    if len(request.job_description) < 100:
        raise HTTPException(status_code=400, detail="Job description must be at least 100 characters")
    
    depth_level = "ready" if request.mode == "quick" else "full"
    interviewer_type = request.interviewer_type if request.interviewer_type in ["hr", "technical", "manager", "general"] else "general"
    
    try:
        system_prompt = await get_combined_prompt(interviewer_type, depth_level)
        
        max_tokens = 2000 if depth_level == "ready" else 4000
        
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"Analyze this job description:\n\n{request.job_description}"
            }]
        )
        
        analysis_text = message.content[0].text if message.content else "Unable to generate analysis"
        
        return AnalyzeJobResponse(
            analysis=analysis_text,
            mode=request.mode
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
