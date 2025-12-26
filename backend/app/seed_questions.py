import os
import logging
from supabase import create_client, Client
from .static_questions import INTERVIEW_QUESTIONS, QUESTIONS_TO_ASK

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return create_client(url, key)
    return None

def seed_interview_questions():
    supabase = get_supabase_client()
    if not supabase:
        logger.error("Supabase client not available")
        return False
    
    try:
        existing = supabase.table('interview_questions').select('id').limit(1).execute()
        if existing.data and len(existing.data) > 0:
            logger.info("Interview questions already exist. Skipping seed.")
            return True
        
        for question in INTERVIEW_QUESTIONS:
            question_with_defaults = {**question, "is_active": True}
            supabase.table('interview_questions').insert(question_with_defaults).execute()
        
        logger.info(f"Successfully seeded {len(INTERVIEW_QUESTIONS)} interview questions")
        return True
    except Exception as e:
        logger.error(f"Failed to seed interview questions: {e}")
        return False

def seed_questions_to_ask():
    supabase = get_supabase_client()
    if not supabase:
        logger.error("Supabase client not available")
        return False
    
    try:
        existing = supabase.table('questions_to_ask').select('id').limit(1).execute()
        if existing.data and len(existing.data) > 0:
            logger.info("Questions to ask already exist. Skipping seed.")
            return True
        
        for question in QUESTIONS_TO_ASK:
            question_with_defaults = {**question, "is_active": True}
            supabase.table('questions_to_ask').insert(question_with_defaults).execute()
        
        logger.info(f"Successfully seeded {len(QUESTIONS_TO_ASK)} questions to ask")
        return True
    except Exception as e:
        logger.error(f"Failed to seed questions to ask: {e}")
        return False

def seed_all():
    logger.info("Starting database seeding...")
    q1 = seed_interview_questions()
    q2 = seed_questions_to_ask()
    
    if q1 and q2:
        logger.info("Database seeding completed successfully!")
        return True
    else:
        logger.error("Database seeding completed with errors")
        return False
