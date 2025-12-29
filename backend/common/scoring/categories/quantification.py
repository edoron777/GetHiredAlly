"""
Quantification scoring category.
Max: 20 points
"""

from ..config import CATEGORY_WEIGHTS


def calculate_quantification_score(data) -> float:
    """
    Calculate quantification score based on % of bullets with numbers.
    
    Scoring logic:
    - 80%+ bullets with numbers: 20 points
    - 60-79%: 16 points
    - 40-59%: 12 points
    - 20-39%: 8 points
    - Below 20%: 4 points
    """
    # Handle both dict and dataclass
    if isinstance(data, dict):
        total_bullets = data.get("total_bullet_points", 0)
        bullets_with_numbers = data.get("bullets_with_numbers", 0)
    else:
        total_bullets = data.total_bullet_points
        bullets_with_numbers = data.bullets_with_numbers
    
    if total_bullets == 0:
        return 10.0  # Neutral if no bullets detected
    
    ratio = bullets_with_numbers / total_bullets
    
    if ratio >= 0.80:
        return 20.0
    elif ratio >= 0.60:
        return 16.0
    elif ratio >= 0.40:
        return 12.0
    elif ratio >= 0.20:
        return 8.0
    else:
        return 4.0
