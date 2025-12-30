"""
Experience scoring category.
Max: 20 points (v3.0)
"""

def calculate_experience_score(data: dict) -> float:
    """
    Calculate experience presentation score.
    
    Args:
        data: dict with experience-related fields
        
    Returns:
        Score between 0 and 20
    """
    score = 0.0
    
    # Reverse chronological order (5 points)
    if data.get('is_reverse_chronological', False):
        score += 5.0
    
    # Company names present (4 points)
    if data.get('has_company_names', False):
        score += 4.0
    
    # Job titles present (4 points)
    if data.get('has_job_titles', False):
        score += 4.0
    
    # Dates for each role (4 points)
    if data.get('has_dates_for_each_role', False):
        score += 4.0
    
    # Consistent date format (3 points)
    if data.get('dates_are_consistent_format', False):
        score += 3.0
    
    return score
