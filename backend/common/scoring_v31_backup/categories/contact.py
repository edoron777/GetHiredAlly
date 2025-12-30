"""
Contact information scoring category.
Max: 5 points (v3.0)
Basic hygiene - LinkedIn removed from scoring.
"""

def calculate_contact_score(data: dict) -> float:
    """
    Calculate contact information score.
    
    Note: LinkedIn removed - it's optional, not required.
    
    Args:
        data: dict with contact fields
        
    Returns:
        Score between 0 and 5
    """
    score = 0.0
    
    # Email present (2 points)
    if data.get('has_email', False):
        score += 2.0
    
    # Phone present (2 points)
    if data.get('has_phone', False):
        score += 2.0
    
    # Professional email (1 point)
    if data.get('email_is_professional', False):
        score += 1.0
    
    return score
