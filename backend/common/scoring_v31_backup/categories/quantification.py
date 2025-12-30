"""
Quantification scoring category.
Max: 25 points (v3.0)
THE most important category - achievements with numbers.
"""

def calculate_quantification_score(data: dict) -> float:
    """
    Calculate quantification score based on % of bullets with numbers.
    
    Args:
        data: dict with 'total_bullet_points' and 'bullets_with_numbers'
        
    Returns:
        Score between 5 and 25
    """
    total_bullets = data.get('total_bullet_points', 0)
    bullets_with_numbers = data.get('bullets_with_numbers', 0)
    
    if total_bullets == 0:
        return 12.5  # Neutral if no bullets detected
    
    ratio = bullets_with_numbers / total_bullets
    
    if ratio >= 0.70:
        return 25.0
    elif ratio >= 0.50:
        return 20.0
    elif ratio >= 0.35:
        return 15.0
    elif ratio >= 0.20:
        return 10.0
    else:
        return 5.0
