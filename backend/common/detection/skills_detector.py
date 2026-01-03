"""
Skills Section Detector
=======================
Issues Detected:
- FORMAT_SKILLS_SECTION_MISSING
- FORMAT_SKILLS_SECTION_POSITION

Version: 1.0 | Created: January 3, 2026
"""

import re
from typing import List, Dict, Optional, Tuple
from .word_lists import SKILLS_POSITION_THRESHOLD

SKILLS_HEADER_PATTERNS = [
    r'^\s*skills?\s*$',
    r'^\s*technical\s+skills?\s*$',
    r'^\s*core\s+skills?\s*$',
    r'^\s*key\s+skills?\s*$',
    r'^\s*core\s+competenc(?:y|ies)\s*$',
    r'^\s*competenc(?:y|ies)\s*$',
    r'^\s*expertise\s*$',
    r'^\s*areas?\s+of\s+expertise\s*$',
    r'^\s*technical\s+expertise\s*$',
    r'^\s*technologies?\s*$',
    r'^\s*tools?\s+(?:and|&)\s+technologies?\s*$',
    r'^\s*proficienc(?:y|ies)\s*$',
]


def find_skills_section(cv_text: str) -> Optional[Tuple[int, int, str]]:
    """Find skills section. Returns (char_position, line_number, header) or None."""
    lines = cv_text.split('\n')
    total_chars = len(cv_text)
    current_pos = 0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        for pattern in SKILLS_HEADER_PATTERNS:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                return (current_pos, i, line_stripped)
        current_pos += len(line) + 1
    
    return None


def detect_skills_section_missing(cv_text: str) -> List[Dict]:
    """Detect missing Skills section."""
    issues = []
    
    if find_skills_section(cv_text) is None:
        issues.append({
            'issue_type': 'FORMAT_SKILLS_SECTION_MISSING',
            'severity': 'critical',
            'location': 'entire document',
            'details': 'No dedicated Skills section found.'
        })
    
    return issues


def detect_skills_section_position(cv_text: str) -> List[Dict]:
    """Detect if Skills section is positioned too far down."""
    issues = []
    
    skills_info = find_skills_section(cv_text)
    
    if skills_info is not None:
        char_position, line_number, header = skills_info
        total_chars = len(cv_text)
        relative_position = char_position / total_chars if total_chars > 0 else 0
        
        if relative_position > SKILLS_POSITION_THRESHOLD:
            position_percentage = int(relative_position * 100)
            issues.append({
                'issue_type': 'FORMAT_SKILLS_SECTION_POSITION',
                'severity': 'consider',
                'location': f'Line {line_number + 1}',
                'details': f'Skills section at {position_percentage}% of CV. Move it higher.'
            })
    
    return issues


def detect_all_skills_issues(cv_text: str) -> List[Dict]:
    """Run all skills-related detections."""
    issues = []
    
    missing_issues = detect_skills_section_missing(cv_text)
    issues.extend(missing_issues)
    
    if not missing_issues:
        issues.extend(detect_skills_section_position(cv_text))
    
    return issues
