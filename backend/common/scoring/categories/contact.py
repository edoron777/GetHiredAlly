"""
Contact information scoring category.
Max: 10 points
"""

from ..config import CATEGORY_WEIGHTS


def calculate_contact_score(data) -> float:
    """
    Calculate contact information score.
    
    Scoring breakdown:
    - Name present: 2 points
    - Email present: 3 points
    - Phone present: 2 points
    - LinkedIn present: 2 points
    - Professional email: 1 point
    """
    score = 0.0
    
    # Handle both dict and dataclass
    if isinstance(data, dict):
        has_name = data.get("has_name", False)
        has_email = data.get("has_email", False)
        has_phone = data.get("has_phone", False)
        has_linkedin = data.get("has_linkedin", False)
        professional_email = data.get("email_is_professional", False)
    else:
        has_name = data.has_name
        has_email = data.has_email
        has_phone = data.has_phone
        has_linkedin = data.has_linkedin
        professional_email = data.email_is_professional
    
    if has_name:
        score += 2.0
    if has_email:
        score += 3.0
    if has_phone:
        score += 2.0
    if has_linkedin:
        score += 2.0
    if professional_email:
        score += 1.0
    
    return score
