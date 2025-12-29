"""
Language scoring category.
Max: 15 points
"""

from ..config import CATEGORY_WEIGHTS


def calculate_language_score(data) -> float:
    """
    Calculate language quality score.
    
    Scoring breakdown:
    - Strong action verbs: 5 points
    - Minimal passive voice: 5 points
    - Minimal weak phrases: 5 points
    """
    score = 0.0
    
    # Handle both dict and dataclass
    if isinstance(data, dict):
        strong_verbs = data.get("strong_action_verbs_count", 0)
        passive_count = data.get("passive_voice_count", 0)
        weak_count = data.get("weak_phrases_count", 0)
    else:
        strong_verbs = data.strong_action_verbs_count
        passive_count = data.passive_voice_count
        weak_count = data.weak_phrases_count
    
    # Strong action verbs used (5 points)
    if strong_verbs >= 10:
        score += 5.0
    elif strong_verbs >= 7:
        score += 4.0
    elif strong_verbs >= 4:
        score += 3.0
    elif strong_verbs >= 1:
        score += 2.0
    
    # Minimal passive voice (5 points)
    if passive_count == 0:
        score += 5.0
    elif passive_count <= 2:
        score += 4.0
    elif passive_count <= 4:
        score += 2.0
    
    # Minimal weak phrases (5 points)
    if weak_count == 0:
        score += 5.0
    elif weak_count <= 2:
        score += 4.0
    elif weak_count <= 4:
        score += 2.0
    
    return score
