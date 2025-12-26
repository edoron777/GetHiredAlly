import os
import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from supabase import create_client, Client
from .static_questions import INTERVIEW_QUESTIONS, QUESTIONS_TO_ASK

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/questions", tags=["questions"])

def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return create_client(url, key)
    return None

class QuestionsResponse(BaseModel):
    questions: List[dict]
    questions_to_ask: List[dict]
    total_count: int

@router.get("/static", response_model=QuestionsResponse)
async def get_static_questions(
    category: Optional[str] = Query(None, description="Filter by category"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    interviewer_type: Optional[str] = Query(None, description="Filter by interviewer type"),
    depth_level: Optional[str] = Query(None, description="Filter by depth level")
):
    supabase = get_supabase_client()
    
    questions = []
    questions_to_ask = []
    
    if supabase:
        try:
            query = supabase.table('interview_questions').select('*').eq('is_active', True)
            
            if category:
                query = query.eq('category', category)
            if subcategory:
                query = query.eq('subcategory', subcategory)
            
            result = query.order('order_priority').execute()
            
            if result.data:
                questions = result.data
                
                if interviewer_type:
                    questions = [q for q in questions if interviewer_type in q.get('interviewer_types', [])]
                if depth_level:
                    questions = [q for q in questions if depth_level in q.get('depth_levels', [])]
            
            ask_result = supabase.table('questions_to_ask').select('*').eq('is_active', True).order('order_priority').execute()
            if ask_result.data:
                questions_to_ask = ask_result.data
                
        except Exception as e:
            logger.warning(f"Error fetching from database: {e}. Using static data.")
            questions = get_filtered_static_questions(category, subcategory, interviewer_type, depth_level)
            questions_to_ask = QUESTIONS_TO_ASK
    else:
        logger.info("Supabase not available. Using static data.")
        questions = get_filtered_static_questions(category, subcategory, interviewer_type, depth_level)
        questions_to_ask = QUESTIONS_TO_ASK
    
    return QuestionsResponse(
        questions=questions,
        questions_to_ask=questions_to_ask,
        total_count=len(questions)
    )

def get_filtered_static_questions(category, subcategory, interviewer_type, depth_level):
    questions = INTERVIEW_QUESTIONS.copy()
    
    if category:
        questions = [q for q in questions if q.get('category') == category]
    if subcategory:
        questions = [q for q in questions if q.get('subcategory') == subcategory]
    if interviewer_type:
        questions = [q for q in questions if interviewer_type in q.get('interviewer_types', [])]
    if depth_level:
        questions = [q for q in questions if depth_level in q.get('depth_levels', [])]
    
    return sorted(questions, key=lambda x: x.get('order_priority', 999))

@router.post("/seed")
async def seed_questions():
    from .seed_questions import seed_all
    success = seed_all()
    
    if success:
        return {"status": "success", "message": "Questions seeded successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to seed questions")

@router.get("/categories")
async def get_categories():
    categories = set()
    subcategories = {}
    
    for q in INTERVIEW_QUESTIONS:
        cat = q.get('category')
        subcat = q.get('subcategory')
        
        if cat:
            categories.add(cat)
            if cat not in subcategories:
                subcategories[cat] = set()
            if subcat:
                subcategories[cat].add(subcat)
    
    return {
        "categories": sorted(list(categories)),
        "subcategories": {k: sorted(list(v)) for k, v in subcategories.items()}
    }
