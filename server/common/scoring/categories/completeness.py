"""
Completeness Scoring (12 points)
- Contact Information: 4 points
- Required Sections: 3 points
- Keywords & Skills: 2 points
- Job Entry Standards: 3 points

DETERMINISTIC: Same input = Same score.
"""

from typing import Dict, Any
from ..config import COMPLETENESS_WEIGHTS


def score_completeness(extracted_data: Dict[str, Any]) -> float:
    """
    Calculate Completeness score (max 12 points).
    
    DETERMINISTIC: Same extracted_data = Same score.
    """
    score = 0.0
    
    score += _score_contact_info(extracted_data)
    score += _score_required_sections(extracted_data)
    score += _score_keywords_skills(extracted_data)
    score += _score_job_entry_standards(extracted_data)
    
    return max(0, min(12, score))


def _score_contact_info(data: Dict[str, Any]) -> float:
    """Score contact information (max 4 points)."""
    max_points = COMPLETENESS_WEIGHTS['contact_info']
    score = 0.0
    
    contact = data.get('contact', {})
    
    # Has name (1 point)
    if contact.get('has_name', False):
        score += 1.0
    
    # Has email (1 point)
    if contact.get('has_email', False):
        score += 1.0
    
    # Has phone (0.8 points)
    if contact.get('has_phone', False):
        score += 0.8
    
    # Has LinkedIn (0.7 points)
    if contact.get('has_linkedin', False):
        score += 0.7
    
    # Professional email (0.5 points) - deduct if unprofessional
    if contact.get('has_email', False) and not contact.get('email_is_professional', True):
        score -= 0.5
    
    return min(max_points, max(0, score))


def _score_required_sections(data: Dict[str, Any]) -> float:
    """Score required sections (max 3 points)."""
    max_points = COMPLETENESS_WEIGHTS['required_sections']
    score = 0.0
    
    structure = data.get('structure', {})
    
    # Has Experience section (1.5 points)
    if structure.get('has_experience_section', False):
        score += 1.5
    
    # Has Education section (0.8 points)
    if structure.get('has_education_section', False):
        score += 0.8
    
    # Has Skills section (0.7 points)
    if structure.get('has_skills_section', False):
        score += 0.7
    
    return min(max_points, score)


def _score_keywords_skills(data: Dict[str, Any]) -> float:
    """Score keywords and skills (max 2 points)."""
    max_points = COMPLETENESS_WEIGHTS['keywords_skills']
    score = 0.0
    
    skills = data.get('skills', {})
    
    # Has technical keywords (1 point if >= 10)
    keyword_count = skills.get('tech_keywords_count', 0)
    if keyword_count >= 10:
        score += 1.0
    elif keyword_count >= 5:
        score += 0.5
    
    # Skills are categorized (0.5 points)
    if skills.get('skills_are_categorized', False):
        score += 0.5
    
    # Has industry-relevant terms (0.5 points)
    if skills.get('has_industry_terms', False):
        score += 0.5
    
    return min(max_points, score)


def _score_job_entry_standards(data: Dict[str, Any]) -> float:
    """Score job entry standards (max 3 points)."""
    max_points = COMPLETENESS_WEIGHTS['job_entry_standards']
    
    experience = data.get('experience', {})
    
    # Start with full points, deduct for missing elements
    score = max_points
    
    # Missing job titles (-0.5)
    if not experience.get('all_have_titles', True):
        score -= 0.5
    
    # Missing company names (-0.5)
    if not experience.get('all_have_companies', True):
        score -= 0.5
    
    # Missing dates (-0.4)
    if not experience.get('all_have_dates', True):
        score -= 0.4
    
    # Dates not on same line (-0.3)
    if not experience.get('dates_formatted_well', True):
        score -= 0.3
    
    return max(0, score)
