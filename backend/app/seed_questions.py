import os
import logging
from supabase import create_client, Client
from .static_questions import INTERVIEW_QUESTIONS, QUESTIONS_TO_ASK, CATEGORY_DESCRIPTIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return create_client(url, key)
    return None

INTERVIEW_QUESTIONS_COLUMNS = [
    "category", "question_text", "why_they_ask", "framework", 
    "good_answer_example", "what_to_avoid", "order_priority", "is_active"
]

QUESTIONS_TO_ASK_COLUMNS = [
    "category", "question_text", "order_priority", "is_active", "purpose", 
    "why_to_ask", "what_to_listen_for", "warning_signs"
]

def filter_columns(data, allowed_columns):
    return {k: v for k, v in data.items() if k in allowed_columns}

def seed_categories():
    supabase = get_supabase_client()
    if not supabase:
        logger.error("Supabase client not available")
        return False
    
    try:
        supabase.table('question_categories').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        
        for cat in CATEGORY_DESCRIPTIONS:
            supabase.table('question_categories').insert(cat).execute()
        
        logger.info(f"Successfully seeded {len(CATEGORY_DESCRIPTIONS)} categories")
        return True
    except Exception as e:
        logger.error(f"Failed to seed categories: {e}")
        return False

def seed_interview_questions(force=False):
    supabase = get_supabase_client()
    if not supabase:
        logger.error("Supabase client not available")
        return False
    
    try:
        if force:
            supabase.table('interview_questions').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            logger.info("Cleared existing interview questions")
        else:
            existing = supabase.table('interview_questions').select('id').limit(1).execute()
            if existing.data and len(existing.data) > 0:
                logger.info("Interview questions already exist. Skipping seed. Use force=True to replace.")
                return True
        
        for question in INTERVIEW_QUESTIONS:
            question_data = filter_columns(question, INTERVIEW_QUESTIONS_COLUMNS)
            question_data["is_active"] = True
            supabase.table('interview_questions').insert(question_data).execute()
        
        logger.info(f"Successfully seeded {len(INTERVIEW_QUESTIONS)} interview questions")
        return True
    except Exception as e:
        logger.error(f"Failed to seed interview questions: {e}")
        return False

def seed_questions_to_ask(force=False):
    supabase = get_supabase_client()
    if not supabase:
        logger.error("Supabase client not available")
        return False
    
    try:
        if force:
            supabase.table('questions_to_ask').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            logger.info("Cleared existing questions to ask")
        else:
            existing = supabase.table('questions_to_ask').select('id').limit(1).execute()
            if existing.data and len(existing.data) > 0:
                logger.info("Questions to ask already exist. Skipping seed. Use force=True to replace.")
                return True
        
        for question in QUESTIONS_TO_ASK:
            question_data = filter_columns(question, QUESTIONS_TO_ASK_COLUMNS)
            question_data["is_active"] = True
            if "why_ask" in question:
                question_data["why_to_ask"] = question["why_ask"]
            question_data["purpose"] = question.get("category", "general")
            supabase.table('questions_to_ask').insert(question_data).execute()
        
        logger.info(f"Successfully seeded {len(QUESTIONS_TO_ASK)} questions to ask")
        return True
    except Exception as e:
        logger.error(f"Failed to seed questions to ask: {e}")
        return False

def seed_all(force=False):
    logger.info("Starting database seeding...")
    c = seed_categories()
    q1 = seed_interview_questions(force=force)
    q2 = seed_questions_to_ask(force=force)
    
    success = q1 and q2
    if success:
        logger.info("Database seeding completed successfully!")
    else:
        logger.warning("Database seeding completed with some errors (categories optional)")
    
    return success
