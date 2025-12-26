import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic
from supabase import create_client, Client

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
    mode: str  # "quick", "deep", or "max"

class AnalyzeJobResponse(BaseModel):
    analysis: str
    mode: str

def get_mode_instructions(mode: str) -> str:
    if mode == "quick":
        return "\n\nProvide a CONCISE analysis focusing on the top 3-5 most important points in each category. Keep your response under 800 words. Be direct and actionable."
    elif mode == "deep":
        return "\n\nProvide a COMPREHENSIVE analysis with detailed explanations for each point. Include specific examples and actionable advice. Your response should be thorough but organized (1500-2000 words)."
    elif mode == "max":
        return "\n\nProvide an EXHAUSTIVE analysis leaving no stone unturned. Include:\n- Detailed breakdown of every requirement\n- Hidden meanings and implications in the language used\n- Salary negotiation insights based on the role level\n- Questions to ask in the interview\n- Potential career growth paths\n- Industry-specific insights\n- How to stand out from other candidates\n\nBe extremely thorough and comprehensive (2500+ words)."
    return ""

async def get_system_prompt_from_db(mode: str) -> str:
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    result = supabase.table('prompt_templates').select('content').eq('service_name', 'xray_analyzer').eq('template_type', 'system').single().execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="System prompt not found in database")
    
    base_prompt = result.data['content']
    return base_prompt + get_mode_instructions(mode)

@router.post("/analyze-job", response_model=AnalyzeJobResponse)
async def analyze_job(request: AnalyzeJobRequest):
    if len(request.job_description) < 100:
        raise HTTPException(status_code=400, detail="Job description must be at least 100 characters")
    
    if request.mode not in ["quick", "deep", "max"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Must be 'quick', 'deep', or 'max'")
    
    try:
        system_prompt = await get_system_prompt_from_db(request.mode)
        
        max_tokens_map = {
            "quick": 2048,
            "deep": 4096,
            "max": 8192
        }
        
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=max_tokens_map.get(request.mode, 4096),
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"Please analyze this job description:\n\n{request.job_description}"
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
