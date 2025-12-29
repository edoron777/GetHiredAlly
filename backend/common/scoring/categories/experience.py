"""
Experience section scoring category.
Max: 10 points
"""

from ..config import CATEGORY_WEIGHTS


def calculate_experience_score(data) -> float:
    """
    Calculate experience presentation score.
    
    Scoring breakdown:
    - Reverse chronological order: 3 points
    - Company names present: 2 points
    - Job titles present: 2 points
    - Dates for each role: 3 points
    """
    score = 0.0
    
    # Handle both dict and dataclass
    if isinstance(data, dict):
        reverse_chrono = data.get("is_reverse_chronological", False)
        has_companies = data.get("has_company_names", False)
        has_titles = data.get("has_job_titles", False)
        has_dates = data.get("has_dates_for_each_role", False)
    else:
        reverse_chrono = data.is_reverse_chronological
        has_companies = data.has_company_names
        has_titles = data.has_job_titles
        has_dates = data.has_dates_for_each_role
    
    if reverse_chrono:
        score += 3.0
    if has_companies:
        score += 2.0
    if has_titles:
        score += 2.0
    if has_dates:
        score += 3.0
    
    return score
