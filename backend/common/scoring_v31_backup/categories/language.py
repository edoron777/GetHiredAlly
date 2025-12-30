"""
Language scoring category.
Max: 15 points (v3.0)
"""

def calculate_language_score(data: dict) -> float:
    """
    Calculate language quality score.
    
    Args:
        data: dict with language metrics
        
    Returns:
        Score between 0 and 15
    """
    score = 0.0
    
    # Strong action verbs (6 points)
    strong_count = data.get('strong_action_verbs_count', 0)
    if strong_count >= 10:
        score += 6.0
    elif strong_count >= 7:
        score += 5.0
    elif strong_count >= 4:
        score += 3.5
    elif strong_count >= 1:
        score += 2.0
    
    # Minimal weak phrases (5 points)
    weak_count = data.get('weak_phrases_count', 0)
    if weak_count == 0:
        score += 5.0
    elif weak_count <= 2:
        score += 4.0
    elif weak_count <= 4:
        score += 2.0
    
    # Minimal passive voice (4 points)
    passive_count = data.get('passive_voice_count', 0)
    if passive_count == 0:
        score += 4.0
    elif passive_count <= 2:
        score += 3.0
    elif passive_count <= 4:
        score += 1.5
    
    return score
