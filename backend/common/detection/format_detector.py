"""
Format and Consistency Detector

Detects formatting inconsistencies using pattern matching.
100% CODE - No AI - Deterministic results.
"""

import re
from typing import List, Dict, Set
from collections import Counter


DATE_FORMATS = {
    'month_year_full': re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', re.IGNORECASE),
    'month_year_abbr': re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[.]?\s+\d{4}\b', re.IGNORECASE),
    'mm_yyyy': re.compile(r'\b(?:0?[1-9]|1[0-2])/\d{4}\b'),
    'mm_yy': re.compile(r'\b(?:0?[1-9]|1[0-2])/\d{2}\b'),
    'yyyy_mm': re.compile(r'\b\d{4}[-/](?:0?[1-9]|1[0-2])\b'),
    'year_only': re.compile(r'\b(?:19|20)\d{2}\b'),
}

BULLET_STYLES = {
    'dash': re.compile(r'^\s*-\s+', re.MULTILINE),
    'bullet': re.compile(r'^\s*•\s*', re.MULTILINE),
    'asterisk': re.compile(r'^\s*\*\s+', re.MULTILINE),
    'arrow': re.compile(r'^\s*>\s+', re.MULTILINE),
    'number': re.compile(r'^\s*\d+[.)]\s+', re.MULTILINE),
}


def detect_date_inconsistency(text: str) -> List[Dict]:
    """
    Detect inconsistent date formats.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of DATE_FORMAT_INCONSISTENT issues
    """
    issues = []
    formats_found = {}
    
    for format_name, pattern in DATE_FORMATS.items():
        matches = pattern.findall(text)
        if matches:
            formats_found[format_name] = matches
    
    if len(formats_found) > 1:
        examples = []
        for fmt, matches in formats_found.items():
            examples.append(matches[0])
        
        issues.append({
            'issue_type': 'FORMAT_INCONSISTENT_DATES',
            'location': 'Throughout CV',
            'description': f'Multiple date formats used ({len(formats_found)} different formats)',
            'current': ', '.join(examples[:3]),
            'suggestion': 'Use a consistent date format throughout (e.g., "Jan 2020" or "January 2020")',
        })
    
    return issues


def detect_bullet_inconsistency(text: str) -> List[Dict]:
    """
    Detect inconsistent bullet point styles.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of FORMAT_INCONSISTENT issues
    """
    issues = []
    styles_found = {}
    
    for style_name, pattern in BULLET_STYLES.items():
        matches = pattern.findall(text)
        if matches:
            styles_found[style_name] = len(matches)
    
    if len(styles_found) > 1:
        issues.append({
            'issue_type': 'FORMAT_INCONSISTENT_BULLETS',
            'location': 'Bullet Points',
            'description': f'Inconsistent bullet styles ({len(styles_found)} different styles: {", ".join(styles_found.keys())})',
            'current': ', '.join(styles_found.keys()),
            'suggestion': 'Use a consistent bullet style throughout',
        })
    
    return issues


def detect_whitespace_issues(text: str) -> List[Dict]:
    """
    Detect whitespace problems.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of WHITESPACE_ISSUE issues
    """
    issues = []
    
    if re.search(r'\n{4,}', text):
        issues.append({
            'issue_type': 'FORMAT_EXCESSIVE_BLANK_LINES',
            'location': 'Throughout CV',
            'description': 'Excessive blank lines detected',
            'suggestion': 'Remove extra blank lines for cleaner appearance',
        })
    
    trailing_count = len(re.findall(r'[ \t]+$', text, re.MULTILINE))
    if trailing_count > 5:
        issues.append({
            'issue_type': 'FORMAT_TRAILING_WHITESPACE',
            'location': 'Throughout CV',
            'description': f'Trailing whitespace on {trailing_count} lines',
            'suggestion': 'Remove trailing spaces for cleaner formatting',
        })
    
    indents = re.findall(r'^[ \t]+', text, re.MULTILINE)
    if indents:
        indent_sizes = [len(i.replace('\t', '    ')) for i in indents]
        unique_indents = len(set(indent_sizes))
        
        if unique_indents > 3:
            issues.append({
                'issue_type': 'FORMAT_INCONSISTENT_SPACING',
                'location': 'Indentation',
                'description': f'Inconsistent indentation ({unique_indents} different levels)',
                'suggestion': 'Use consistent indentation throughout',
            })
    
    return issues


def detect_format_issues(text: str) -> List[Dict]:
    """
    Detect all formatting issues.
    
    This is the MAIN function for format analysis.
    100% deterministic - same text → same result.
    
    Args:
        text: Full CV text
        
    Returns:
        List of formatting issues
    """
    issues = []
    
    issues.extend(detect_date_inconsistency(text))
    issues.extend(detect_bullet_inconsistency(text))
    issues.extend(detect_whitespace_issues(text))
    
    return issues
