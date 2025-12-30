"""
Regex patterns for CV text analysis.
"""

import re
from typing import Dict

# Email pattern
EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

# Phone patterns (various formats)
PHONE_PATTERN = re.compile(
    r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
)

# LinkedIn URL pattern
LINKEDIN_PATTERN = re.compile(r'linkedin\.com/in/[\w-]+', re.IGNORECASE)

# Number pattern (for quantification)
NUMBER_PATTERN = re.compile(
    r'\d+%|\$\d+[\d,]*|\d+\s*(users|customers|employees|projects|years|months|clients|members|people|team)'
)

# Weak phrases to detect
WEAK_PHRASES = [
    r'responsible for',
    r'duties included',
    r'worked on',
    r'helped with',
    r'was part of',
    r'assisted in',
    r'involved in'
]
WEAK_PHRASES_PATTERN = re.compile('|'.join(WEAK_PHRASES), re.IGNORECASE)

# Strong action verbs
STRONG_VERBS = [
    'led', 'managed', 'developed', 'created', 'built', 'designed',
    'implemented', 'launched', 'increased', 'decreased', 'reduced',
    'improved', 'optimized', 'achieved', 'delivered', 'established',
    'generated', 'negotiated', 'streamlined', 'transformed', 'spearheaded',
    'orchestrated', 'pioneered', 'accelerated', 'maximized', 'minimized'
]
STRONG_VERBS_PATTERN = re.compile(r'\b(' + '|'.join(STRONG_VERBS) + r')\b', re.IGNORECASE)

# Passive voice indicators
PASSIVE_INDICATORS = [
    r'was\s+\w+ed\b',
    r'were\s+\w+ed\b',
    r'been\s+\w+ed\b',
    r'being\s+\w+ed\b'
]
PASSIVE_PATTERN = re.compile('|'.join(PASSIVE_INDICATORS), re.IGNORECASE)

# Section headers
SECTION_HEADERS = [
    'experience', 'education', 'skills', 'summary', 'objective',
    'projects', 'certifications', 'achievements', 'awards',
    'work history', 'employment', 'professional experience'
]
SECTION_PATTERN = re.compile(
    r'^(' + '|'.join(SECTION_HEADERS) + r')\s*:?\s*$',
    re.IGNORECASE | re.MULTILINE
)


def extract_patterns(text: str) -> Dict:
    """
    Extract various patterns from CV text.
    
    Returns:
        Dictionary with detected patterns and counts
    """
    return {
        "has_email": bool(EMAIL_PATTERN.search(text)),
        "has_phone": bool(PHONE_PATTERN.search(text)),
        "has_linkedin": bool(LINKEDIN_PATTERN.search(text)),
        "bullets_with_numbers": len(NUMBER_PATTERN.findall(text)),
        "weak_phrases_count": len(WEAK_PHRASES_PATTERN.findall(text)),
        "strong_action_verbs_count": len(STRONG_VERBS_PATTERN.findall(text)),
        "passive_voice_count": len(PASSIVE_PATTERN.findall(text)),
        "has_section_headers": bool(SECTION_PATTERN.search(text)),
        "section_headers_found": SECTION_PATTERN.findall(text)
    }
