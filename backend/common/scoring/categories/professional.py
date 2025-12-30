"""
Professional Standards Scoring (8 points)
- Length Appropriateness: 2 points
- Recency & Relevance: 3 points
- Certifications & Education: 3 points

DETERMINISTIC: Same input = Same score.
"""

from typing import Dict, Any
from ..config import PROFESSIONAL_WEIGHTS


def score_professional(extracted_data: Dict[str, Any]) -> float:
    """
    Calculate Professional Standards score (max 8 points).
    
    DETERMINISTIC: Same extracted_data = Same score.
    """
    score = 0.0
    
    score += _score_length(extracted_data)
    score += _score_recency_relevance(extracted_data)
    score += _score_certifications(extracted_data)
    
    return max(0, min(8, score))


def _score_length(data: Dict[str, Any]) -> float:
    """Score CV length appropriateness (max 2 points)."""
    max_points = PROFESSIONAL_WEIGHTS['length']
    
    structure = data.get('structure', {})
    word_count = structure.get('word_count', 0)
    page_count = structure.get('page_count', 1)
    
    score = max_points
    
    # Word count check
    if word_count < 200:
        score -= 1.0  # Too short
    elif word_count > 1200:
        score -= 0.5  # Too long
    
    # Page count check
    if page_count > 2:
        score -= 0.5  # Too many pages
    
    return max(0, score)


def _score_recency_relevance(data: Dict[str, Any]) -> float:
    """Score recency and relevance (max 3 points)."""
    max_points = PROFESSIONAL_WEIGHTS['recency_relevance']
    score = max_points
    
    experience = data.get('experience', {})
    
    # Employment gaps > 6 months (-0.8)
    gaps = experience.get('gaps_detected', [])
    significant_gaps = [g for g in gaps if g.get('months', 0) > 6]
    if significant_gaps:
        score -= 0.8
    
    # Not in reverse chronological order (-0.5)
    if not experience.get('is_reverse_chronological', True):
        score -= 0.5
    
    # Experience older than 10 years emphasized (-0.4)
    if experience.get('old_experience_emphasized', False):
        score -= 0.4
    
    # Outdated technologies listed (-0.3)
    if experience.get('has_outdated_tech', False):
        score -= 0.3
    
    return max(0, score)


def _score_certifications(data: Dict[str, Any]) -> float:
    """Score certifications and education (max 3 points)."""
    max_points = PROFESSIONAL_WEIGHTS['certifications']
    score = 0.0
    
    education = data.get('education', {})
    
    # Has relevant certifications (0.8 points)
    if education.get('has_relevant_certifications', False):
        score += 0.8
    
    # Certifications have dates (0.5 points)
    if education.get('certifications_have_dates', True):
        score += 0.5
    
    # Education complete (degree, school, year) (0.6 points)
    if education.get('education_complete', False):
        score += 0.6
    
    # Education not over-detailed (0.4 points)
    if education.get('education_concise', True):
        score += 0.4
    
    # GPA only if strong or omitted (0.3 points)
    gpa = education.get('gpa_value', None)
    if gpa is None or gpa >= 3.5:
        score += 0.3
    
    return min(max_points, score)
