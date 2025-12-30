"""
Formatting scoring category.
Max: 10 points (v3.0)
"""

def calculate_formatting_score(data: dict) -> float:
    """
    Calculate formatting and structure score.
    
    Args:
        data: dict with formatting fields
        
    Returns:
        Score between 0 and 10
    """
    score = 0.0
    
    # Clear section headers (3 points)
    if data.get('has_section_headers', False):
        score += 3.0
    
    # Uses bullet points (3 points)
    if data.get('uses_bullet_points', False):
        score += 3.0
    
    # Appropriate word count (2 points)
    word_count = data.get('word_count', 0)
    if 400 <= word_count <= 800:
        score += 2.0
    elif 300 <= word_count <= 1000:
        score += 1.0
    
    # Consistent date format (2 points)
    if data.get('dates_are_consistent_format', False):
        score += 2.0
    
    return score
