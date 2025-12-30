"""
Main CV Scoring Calculator v3.0
DETERMINISTIC: Same input ALWAYS produces same output.
"""

from typing import Dict
from .config import SCORE_MIN, SCORE_MAX, GRADE_THRESHOLDS, GRADE_MESSAGES, SCORING_VERSION
from .categories import (
    calculate_quantification_score,
    calculate_experience_score,
    calculate_language_score,
    calculate_grammar_score,
    calculate_skills_score,
    calculate_formatting_score,
    calculate_contact_score,
    calculate_length_score
)


def calculate_cv_score(data: Dict) -> Dict:
    """
    Calculate CV score from extracted data.
    
    THIS FUNCTION IS DETERMINISTIC.
    Same input will ALWAYS produce same output.
    
    Args:
        data: Dictionary with extracted CV data
        
    Returns:
        Dictionary with total_score, breakdown, grade, and message
    """
    
    # Calculate each category score (ordered by weight)
    breakdown = {
        "quantification": calculate_quantification_score(data),  # 25 max
        "experience": calculate_experience_score(data),          # 20 max
        "language": calculate_language_score(data),              # 15 max
        "grammar": calculate_grammar_score(data),                # 10 max
        "skills": calculate_skills_score(data),                  # 10 max
        "formatting": calculate_formatting_score(data),          # 10 max
        "contact": calculate_contact_score(data),                # 5 max
        "length": calculate_length_score(data)                   # 5 max
    }
    
    # Calculate total
    raw_total = sum(breakdown.values())
    
    # Apply bounds
    final_score = int(max(SCORE_MIN, min(SCORE_MAX, raw_total)))
    
    # Determine grade and message
    grade, message = _get_grade_and_message(final_score)
    
    return {
        "total_score": final_score,
        "breakdown": breakdown,
        "grade": grade,
        "message": message,
        "version": SCORING_VERSION,
        "max_possible": SCORE_MAX
    }


def _get_grade_and_message(score: int) -> tuple:
    """Get grade and message based on score."""
    if score >= GRADE_THRESHOLDS["excellent"]:
        return "Excellent", GRADE_MESSAGES["excellent"]
    elif score >= GRADE_THRESHOLDS["good"]:
        return "Good", GRADE_MESSAGES["good"]
    elif score >= GRADE_THRESHOLDS["fair"]:
        return "Fair", GRADE_MESSAGES["fair"]
    elif score >= GRADE_THRESHOLDS["needs_work"]:
        return "Needs Work", GRADE_MESSAGES["needs_work"]
    else:
        return "Needs Attention", GRADE_MESSAGES["needs_attention"]
