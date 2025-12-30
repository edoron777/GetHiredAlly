"""
Red Flags & Issues Scoring (4 points)
- Repetition & Redundancy: 2 points
- Critical Red Flags: 2 points

DETERMINISTIC: Same input = Same score.
"""

from typing import Dict, Any
from ..config import RED_FLAGS_WEIGHTS


def score_red_flags(extracted_data: Dict[str, Any]) -> float:
    """
    Calculate Red Flags score (max 4 points).
    
    This is a PENALTY category - start with max, deduct for issues.
    
    DETERMINISTIC: Same extracted_data = Same score.
    """
    score = 4.0  # Start with full points
    
    score -= _calculate_repetition_penalty(extracted_data)
    score -= _calculate_critical_flags_penalty(extracted_data)
    
    return max(0, min(4, score))


def _calculate_repetition_penalty(data: Dict[str, Any]) -> float:
    """Calculate penalty for repetition (max 2 points penalty)."""
    penalty = 0.0
    
    repetition = data.get('repetition', {})
    
    # Words repeated 5+ times (-0.5)
    if repetition.get('has_overused_words', False):
        penalty += 0.5
    
    # Same phrases across jobs (-0.4)
    if repetition.get('has_duplicate_phrases', False):
        penalty += 0.4
    
    # Redundant bullet points (-0.4)
    if repetition.get('has_redundant_bullets', False):
        penalty += 0.4
    
    # Skills repeated in multiple sections (-0.3)
    if repetition.get('skills_duplicated', False):
        penalty += 0.3
    
    # Same achievements restated (-0.4)
    if repetition.get('achievements_restated', False):
        penalty += 0.4
    
    return min(2.0, penalty)


def _calculate_critical_flags_penalty(data: Dict[str, Any]) -> float:
    """Calculate penalty for critical red flags (max 2 points penalty)."""
    penalty = 0.0
    
    red_flags = data.get('red_flags', {})
    
    # Obvious AI-generated content (-0.5)
    if red_flags.get('ai_content_detected', False):
        penalty += 0.5
    
    # Unprofessional email (-0.3)
    if red_flags.get('unprofessional_email', False):
        penalty += 0.3
    
    # Personal info overshare (-0.2)
    if red_flags.get('personal_info_overshare', False):
        penalty += 0.2
    
    # Photo included (US/UK) (-0.1)
    if red_flags.get('has_photo', False):
        penalty += 0.1
    
    # Age/DOB included (-0.1)
    if red_flags.get('has_age_dob', False):
        penalty += 0.1
    
    # "References available" (-0.1)
    if red_flags.get('has_references_line', False):
        penalty += 0.1
    
    # Salary information (-0.2)
    if red_flags.get('has_salary_info', False):
        penalty += 0.2
    
    return min(2.0, penalty)
