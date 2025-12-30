"""
Skills scoring category.
Max: 10 points (v3.0)
"""

def calculate_skills_score(data: dict) -> float:
    """
    Calculate skills presentation score.
    
    Args:
        data: dict with skills-related fields
        
    Returns:
        Score between 0 and 10
    """
    score = 0.0
    
    # Skills section exists (4 points)
    if data.get('has_skills_section', False):
        score += 4.0
    
    # Skills are categorized (3 points)
    if data.get('skills_are_categorized', False):
        score += 3.0
    
    # Relevant keywords found (3 points)
    keywords = data.get('tech_keywords_found', [])
    keywords_count = len(keywords) if isinstance(keywords, list) else 0
    if keywords_count >= 8:
        score += 3.0
    elif keywords_count >= 5:
        score += 2.0
    elif keywords_count >= 2:
        score += 1.0
    
    return score
