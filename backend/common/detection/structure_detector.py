"""
Structure Detector - Detects CV structural issues

Checks for section order violations that impact ATS scores.
Research shows 15-30% ATS score reduction for incorrect section order.

100% CODE - No AI - Deterministic results.
"""
import re
from typing import Dict, List

SECTION_PATTERNS = {
    'summary': r'(?i)^(professional\s+)?summary|profile|objective|about\s*(me)?',
    'skills': r'(?i)^(technical\s+)?skills|competencies|expertise|technologies',
    'experience': r'(?i)^(professional\s+|work\s+)?experience|employment|work\s+history|career',
    'education': r'(?i)^education|academic|qualifications|degrees?',
    'certifications': r'(?i)^certifications?|licenses?|credentials|accreditations?',
    'projects': r'(?i)^projects?|portfolio|personal\s+projects',
}

EXPECTED_ORDER = ['summary', 'skills', 'experience', 'education', 'certifications', 'projects']


def detect_section_positions(cv_text: str) -> Dict[str, int]:
    """
    Find position (line number) of each section in CV.
    
    Args:
        cv_text: Full CV text
        
    Returns:
        Dict mapping section name to line number
    """
    positions = {}
    lines = cv_text.split('\n')
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        for section, pattern in SECTION_PATTERNS.items():
            if re.match(pattern, line_stripped) and section not in positions:
                positions[section] = i
                break
    
    return positions


def detect_structure_issues(cv_text: str) -> List[Dict]:
    """
    Detect CV structure issues.
    
    Checks for:
    - Education appearing before Experience (major violation)
    - Skills appearing after Education (minor violation)
    
    Returns list of issues with:
    - issue_type: str
    - location: str
    - description: str
    - current: str (section header text for highlighting)
    - is_highlightable: bool
    """
    issues = []
    positions = detect_section_positions(cv_text)
    lines = cv_text.split('\n')
    
    if 'education' in positions and 'experience' in positions:
        if positions['education'] < positions['experience']:
            edu_line = ''
            if positions['education'] < len(lines):
                edu_line = lines[positions['education']].strip()
            
            issues.append({
                'issue_type': 'FORMAT_SECTION_ORDER_VIOLATION',
                'location': 'Document Structure',
                'description': 'Education section appears before Experience section. For experienced professionals, Experience should come first.',
                'current': edu_line,
                'is_highlightable': bool(edu_line),
            })
    
    if 'skills' in positions and 'education' in positions:
        if positions['skills'] > positions['education']:
            skills_line = ''
            if positions['skills'] < len(lines):
                skills_line = lines[positions['skills']].strip()
            
            issues.append({
                'issue_type': 'FORMAT_SECTION_ORDER_VIOLATION',
                'location': 'Document Structure',
                'description': 'Skills section appears after Education. Skills should be near the top for better visibility.',
                'current': skills_line,
                'is_highlightable': bool(skills_line),
            })
    
    if 'skills' in positions and 'experience' in positions:
        if positions['skills'] > positions['experience']:
            skills_line = ''
            if positions['skills'] < len(lines):
                skills_line = lines[positions['skills']].strip()
            
            issues.append({
                'issue_type': 'FORMAT_SECTION_ORDER_VIOLATION',
                'location': 'Document Structure',
                'description': 'Skills section appears after Experience. Consider moving Skills higher for better ATS scanning.',
                'current': skills_line,
                'is_highlightable': bool(skills_line),
            })
    
    return issues
