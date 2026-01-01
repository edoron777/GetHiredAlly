"""
Spelling and Grammar Detector

Detects spelling errors using pyspellchecker.
100% CODE - No AI - Deterministic results.
"""

import re
from typing import List, Dict, Set
from spellchecker import SpellChecker


spell = SpellChecker()

IGNORE_WORDS: Set[str] = {
    'api', 'apis', 'sql', 'html', 'css', 'javascript', 'typescript',
    'python', 'java', 'nodejs', 'react', 'angular', 'vue', 'django',
    'flask', 'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'ci', 'cd',
    'devops', 'saas', 'paas', 'iaas', 'sdk', 'ide', 'ui', 'ux',
    'frontend', 'backend', 'fullstack', 'postgresql', 'mongodb', 'redis',
    'elasticsearch', 'graphql', 'restful', 'microservices', 'agile', 'scrum',
    'jira', 'github', 'gitlab', 'bitbucket', 'jenkins', 'terraform',
    
    'inc', 'ltd', 'llc', 'corp', 'co', 'mgmt', 'dept', 'hr', 'it',
    'ceo', 'cto', 'cfo', 'vp', 'svp', 'evp', 'dir', 'mgr', 'sr', 'jr',
    
    'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec',
    
    'linkedin', 'github', 'gmail', 'mailto', 'href', 'https', 'http', 'www',
}

GRAMMAR_PATTERNS = [
    (re.compile(r'\b(\w+)\s+\1\b', re.IGNORECASE), 'Repeated word: "{}"'),
    (re.compile(r'\.[A-Z]'), 'Missing space after period'),
    (re.compile(r'  +'), 'Multiple consecutive spaces'),
    (re.compile(r'\s+[,.]'), 'Space before punctuation'),
]


def extract_words(text: str) -> List[str]:
    """Extract all words from text for spell checking."""
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    return words


def check_spelling(text: str, max_errors: int = 10) -> List[Dict]:
    """
    Check text for spelling errors.
    
    Args:
        text: Text to check
        max_errors: Maximum errors to return (to avoid overwhelming)
        
    Returns:
        List of spelling error issues
    """
    issues = []
    words = extract_words(text)
    
    found_errors: Set[str] = set()
    
    for word in words:
        if len(word) < 3:
            continue
        
        if word.lower() in IGNORE_WORDS:
            continue
        
        if word.lower() in found_errors:
            continue
        
        if any(c.isdigit() for c in word):
            continue
        
        if word.isupper() and len(word) <= 5:
            continue
        
        if word.lower() not in spell:
            candidates = spell.candidates(word.lower())
            suggestions = list(candidates)[:3] if candidates else []
            
            issues.append({
                'issue_type': 'GRAMMAR_SPELLING_ERROR',
                'location': 'Throughout CV',
                'description': f'Possible spelling error: "{word}"',
                'current': word,
                'suggestion': suggestions[0] if suggestions else None,
            })
            
            found_errors.add(word.lower())
            
            if len(issues) >= max_errors:
                break
    
    return issues


def check_grammar(text: str) -> List[Dict]:
    """
    Check text for common grammar errors using patterns.
    
    Args:
        text: Text to check
        
    Returns:
        List of grammar error issues
    """
    issues = []
    
    for pattern, error_msg in GRAMMAR_PATTERNS:
        matches = pattern.findall(text)
        
        for match in matches[:2]:
            issues.append({
                'issue_type': 'GRAMMAR_GRAMMATICAL_ERROR',
                'location': 'Throughout CV',
                'description': error_msg.format(match) if '{}' in error_msg else error_msg,
                'current': match if isinstance(match, str) else str(match),
            })
    
    return issues


def detect_critical_issues(text: str) -> List[Dict]:
    """
    Detect all critical issues (spelling + grammar).
    
    This is the MAIN function for critical issue detection.
    100% deterministic - same text → same result.
    
    Args:
        text: Full CV text
        
    Returns:
        List of critical issues (SPELLING_ERROR, GRAMMAR_ERROR)
    """
    issues = []
    
    issues.extend(check_spelling(text))
    issues.extend(check_grammar(text))
    
    return issues
