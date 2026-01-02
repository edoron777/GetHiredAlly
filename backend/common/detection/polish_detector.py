"""
Polish and Minor Issues Detector

Detects minor issues for CV polishing.
100% CODE - No AI - Deterministic results.
"""

import re
from typing import List, Dict
from datetime import datetime
from collections import Counter


def detect_outdated_info(text: str, years_threshold: int = 15) -> List[Dict]:
    """
    Detect potentially outdated information (very old dates).
    
    Args:
        text: Text to analyze
        years_threshold: How many years back is considered outdated
        
    Returns:
        List of OUTDATED_INFO issues
    """
    issues = []
    current_year = datetime.now().year
    cutoff_year = current_year - years_threshold
    
    year_pattern = re.compile(r'\b(19\d{2}|20[0-2]\d)\b')
    years = year_pattern.findall(text)
    
    old_years = [y for y in years if int(y) < cutoff_year]
    
    if old_years:
        oldest_year = min(old_years)
        year_match = re.search(r'\b' + oldest_year + r'\b', text)
        current_text = ''
        if year_match:
            start = max(0, year_match.start() - 20)
            end = min(len(text), year_match.end() + 20)
            current_text = text[start:end].strip()
        
        issues.append({
            'issue_type': 'STANDARDS_OUTDATED_INFORMATION',
            'location': 'Throughout CV',
            'description': f'CV contains references to {oldest_year} - consider removing information older than {years_threshold} years',
            'current': current_text if current_text else oldest_year,
            'is_highlightable': bool(current_text),
            'all_instances': sorted(set(old_years)),
            'suggestion': 'Focus on recent experience (last 10-15 years) unless earlier experience is highly relevant',
        })
    
    return issues


def detect_header_inconsistency(text: str) -> List[Dict]:
    """
    Detect inconsistent header capitalization/formatting.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of HEADER_STYLE issues
    """
    issues = []
    
    header_words = ['experience', 'education', 'skills', 'summary', 'profile', 'objective']
    
    styles_found = {
        'uppercase': 0,
        'titlecase': 0,
        'lowercase': 0,
    }
    
    for word in header_words:
        if re.search(r'\b' + word.upper() + r'\b', text):
            styles_found['uppercase'] += 1
        if re.search(r'\b' + word.title() + r'\b', text):
            styles_found['titlecase'] += 1
        if re.search(r'^\s*' + word + r'\s*$', text, re.MULTILINE | re.IGNORECASE):
            styles_found['lowercase'] += 1
    
    active_styles = sum(1 for v in styles_found.values() if v > 0)
    
    if active_styles > 1:
        issues.append({
            'issue_type': 'FORMAT_INCONSISTENT_CAPITALIZATION',
            'location': 'Section Headers',
            'description': 'Inconsistent header capitalization (mix of UPPERCASE and Title Case)',
            'current': '',
            'is_highlightable': False,
            'suggestion': 'Use consistent capitalization for all section headers',
        })
    
    return issues


def detect_repetitive_content(text: str) -> List[Dict]:
    """
    Detect repeated phrases or content.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of REPETITIVE_CONTENT issues
    """
    issues = []
    
    words = text.lower().split()
    phrases = []
    
    for length in [3, 4, 5]:
        for i in range(len(words) - length + 1):
            phrase = ' '.join(words[i:i + length])
            if not any(x in phrase for x in ['and', 'the', 'for', 'with', 'to', 'in', 'of', 'a']):
                phrases.append(phrase)
    
    phrase_counts = Counter(phrases)
    repeated = [(phrase, count) for phrase, count in phrase_counts.items() if count > 1]
    
    if repeated:
        top_repeated = sorted(repeated, key=lambda x: x[1], reverse=True)[:3]
        
        for phrase, count in top_repeated:
            if count >= 2 and len(phrase.split()) >= 3:
                is_in_text = phrase in text.lower()
                issues.append({
                    'issue_type': 'CONTENT_GENERIC_STATEMENTS',
                    'location': 'Throughout CV',
                    'description': f'Phrase repeated {count} times: "{phrase}"',
                    'current': phrase,
                    'is_highlightable': is_in_text,
                    'count': count,
                    'suggestion': 'Vary your language to avoid repetition',
                })
    
    return issues


def detect_polish_issues(text: str) -> List[Dict]:
    """
    Detect all polish/minor issues.
    
    This is the MAIN function for polish analysis.
    100% deterministic - same text → same result.
    
    Args:
        text: Full CV text
        
    Returns:
        List of polish issues
    """
    issues = []
    
    issues.extend(detect_outdated_info(text))
    issues.extend(detect_header_inconsistency(text))
    issues.extend(detect_repetitive_content(text))
    
    return issues
