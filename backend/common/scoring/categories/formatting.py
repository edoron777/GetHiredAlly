"""
Formatting scoring category.
Max: 15 points
"""

from ..config import CATEGORY_WEIGHTS


def calculate_formatting_score(data) -> float:
    """
    Calculate formatting and structure score.
    
    Scoring breakdown:
    - Has clear section headers: 3 points
    - Consistent date format: 3 points
    - Uses bullet points: 3 points
    - Appropriate word count: 3 points
    - ATS friendly (assumed): 3 points
    """
    score = 0.0
    
    # Handle both dict and dataclass
    if isinstance(data, dict):
        has_headers = data.get("has_section_headers", False)
        consistent_dates = data.get("dates_are_consistent_format", False)
        has_bullets = data.get("uses_bullet_points", False)
        word_count = data.get("word_count", 0)
    else:
        has_headers = data.has_section_headers
        consistent_dates = data.dates_are_consistent_format
        has_bullets = data.uses_bullet_points
        word_count = data.word_count
    
    # Has clear section headers (3 points)
    if has_headers:
        score += 3.0
    
    # Consistent date format (3 points)
    if consistent_dates:
        score += 3.0
    
    # Uses bullet points (3 points)
    if has_bullets:
        score += 3.0
    
    # Appropriate word count (3 points)
    if 400 <= word_count <= 800:
        score += 3.0
    elif 300 <= word_count <= 1000:
        score += 2.0
    elif word_count > 0:
        score += 1.0
    
    # ATS friendly - base assumption (3 points)
    score += 3.0
    
    return min(float(CATEGORY_WEIGHTS["formatting"]), score)
