"""
Skills section scoring category.
Max: 10 points
"""

from ..config import CATEGORY_WEIGHTS


def calculate_skills_score(data) -> float:
    """
    Calculate skills presentation score.
    
    Scoring breakdown:
    - Skills section exists: 4 points
    - Skills are categorized: 3 points
    - Relevant tech keywords: 3 points
    """
    score = 0.0
    
    # Handle both dict and dataclass
    if isinstance(data, dict):
        has_skills = data.get("has_skills_section", False)
        categorized = data.get("skills_are_categorized", False)
        keywords = data.get("tech_keywords_found", [])
    else:
        has_skills = data.has_skills_section
        categorized = data.skills_are_categorized
        keywords = data.tech_keywords_found
    
    if has_skills:
        score += 4.0
    
    if categorized:
        score += 3.0
    
    # Relevant tech keywords found (3 points)
    keyword_count = len(keywords) if keywords else 0
    if keyword_count >= 8:
        score += 3.0
    elif keyword_count >= 5:
        score += 2.0
    elif keyword_count >= 2:
        score += 1.0
    
    return score
