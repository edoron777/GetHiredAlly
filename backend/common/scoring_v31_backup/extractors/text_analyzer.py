"""
Text analysis utilities for CV content.
"""

import re
from typing import Dict


def analyze_text(text: str) -> Dict:
    """
    Analyze CV text for various metrics.
    
    Returns:
        Dictionary with text metrics
    """
    # Word count
    words = text.split()
    word_count = len(words)
    
    # Line count
    lines = text.split('\n')
    line_count = len([l for l in lines if l.strip()])
    
    # Bullet points (common formats)
    bullet_patterns = [
        r'^[\s]*[•\-\*\→\►]\s',  # Common bullet characters
        r'^[\s]*\d+[\.\)]\s',     # Numbered lists
    ]
    bullet_count = 0
    for line in lines:
        for pattern in bullet_patterns:
            if re.match(pattern, line):
                bullet_count += 1
                break
    
    # Estimate page count (rough: ~500 words per page)
    estimated_pages = max(1, round(word_count / 500))
    
    return {
        "word_count": word_count,
        "line_count": line_count,
        "total_bullet_points": bullet_count,
        "estimated_page_count": estimated_pages
    }


def check_professional_email(email: str) -> bool:
    """
    Check if email appears professional.
    
    Unprofessional indicators:
    - Contains numbers that look like birth year
    - Contains words like: sexy, hot, cool, babe, etc.
    """
    if not email:
        return False
    
    email_lower = email.lower()
    
    # Unprofessional words
    unprofessional_words = [
        'sexy', 'hot', 'cool', 'babe', 'cutie', 'angel',
        'devil', 'princess', 'prince', 'ninja', 'rockstar',
        'killer', 'crazy', 'mad', '420', '69'
    ]
    
    for word in unprofessional_words:
        if word in email_lower:
            return False
    
    # Check for birth year pattern (19xx or 20xx at end)
    if re.search(r'(19|20)\d{2}@', email_lower):
        return False
    
    return True
