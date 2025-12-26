import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic

router = APIRouter(prefix="/api", tags=["analyze"])

AI_INTEGRATIONS_ANTHROPIC_API_KEY = os.environ.get("AI_INTEGRATIONS_ANTHROPIC_API_KEY")
AI_INTEGRATIONS_ANTHROPIC_BASE_URL = os.environ.get("AI_INTEGRATIONS_ANTHROPIC_BASE_URL")

client = Anthropic(
    api_key=AI_INTEGRATIONS_ANTHROPIC_API_KEY,
    base_url=AI_INTEGRATIONS_ANTHROPIC_BASE_URL
)

class AnalyzeJobRequest(BaseModel):
    job_description: str
    mode: str  # "quick", "deep", or "max"

class AnalyzeJobResponse(BaseModel):
    analysis: str
    mode: str

def get_system_prompt(mode: str) -> str:
    base_prompt = """You are an expert career coach and job description analyst. Your task is to analyze job descriptions and help candidates understand what the employer is really looking for.

When analyzing a job description, identify:
1. **Core Requirements** - The must-have skills and qualifications
2. **Nice-to-Haves** - Skills that would give candidates an edge
3. **Red Flags** - Potential concerns or things to watch out for
4. **Company Culture Signals** - What the language reveals about the work environment
5. **Interview Prep Tips** - Key topics to prepare for based on this role
6. **Keywords to Use** - Important terms to include in your resume/cover letter"""

    if mode == "quick":
        return base_prompt + """

Provide a CONCISE analysis focusing on the top 3-5 most important points in each category. Keep your response under 800 words. Be direct and actionable."""

    elif mode == "deep":
        return base_prompt + """

Provide a COMPREHENSIVE analysis with detailed explanations for each point. Include specific examples and actionable advice. Your response should be thorough but organized (1500-2000 words)."""

    elif mode == "max":
        return base_prompt + """

Provide an EXHAUSTIVE analysis leaving no stone unturned. Include:
- Detailed breakdown of every requirement
- Hidden meanings and implications in the language used
- Salary negotiation insights based on the role level
- Questions to ask in the interview
- Potential career growth paths
- Industry-specific insights
- How to stand out from other candidates

Be extremely thorough and comprehensive (2500+ words)."""

    return base_prompt

@router.post("/analyze-job", response_model=AnalyzeJobResponse)
async def analyze_job(request: AnalyzeJobRequest):
    if len(request.job_description) < 100:
        raise HTTPException(status_code=400, detail="Job description must be at least 100 characters")
    
    if request.mode not in ["quick", "deep", "max"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Must be 'quick', 'deep', or 'max'")
    
    try:
        system_prompt = get_system_prompt(request.mode)
        
        max_tokens_map = {
            "quick": 2048,
            "deep": 4096,
            "max": 8192
        }
        
        message = client.messages.create(
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
