"""
Language Quality Detector

Detects weak verbs, vague descriptions, and buzzword stuffing.
100% CODE - No AI - Deterministic results.
"""

import re
from typing import List, Dict
from .word_lists import (
    WEAK_VERBS,
    BUZZWORDS,
    VAGUE_WORDS,
    BUZZWORD_THRESHOLD,
    VAGUE_THRESHOLD,
)


def detect_weak_verbs(text: str) -> List[Dict]:
    """
    Detect weak action verbs in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of WEAK_ACTION_VERBS issues
    """
    issues = []
    text_lower = text.lower()
    found_verbs = []
    
    for verb in WEAK_VERBS:
        if verb.lower() in text_lower:
            pattern = re.compile(
                r'.{0,30}' + re.escape(verb) + r'.{0,30}',
                re.IGNORECASE
            )
            matches = pattern.findall(text)
            
            for match in matches[:2]:
                if verb.lower() not in [v.lower() for v in found_verbs]:
                    issues.append({
                        'issue_type': 'CONTENT_WEAK_ACTION_VERBS',
                        'location': 'Experience Section',
                        'description': f'Weak/passive phrase detected: "{verb}"',
                        'current': match.strip(),
                        'suggestion': 'Replace with a strong action verb like: led, achieved, delivered, implemented',
                    })
                    found_verbs.append(verb)
    
    return issues


def detect_vague_language(text: str) -> List[Dict]:
    """
    Detect vague/generic language.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of VAGUE_DESCRIPTION issues
    """
    issues = []
    
    vague_count = 0
    found_words = []
    
    for word in VAGUE_WORDS:
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        matches = pattern.findall(text)
        
        if matches:
            vague_count += len(matches)
            found_words.extend(matches)
    
    if vague_count > VAGUE_THRESHOLD:
        unique_words = list(set(found_words))
        issues.append({
            'issue_type': 'CONTENT_GENERIC_STATEMENTS',
            'location': 'Throughout CV',
            'description': f'Too many vague words ({vague_count} found): {", ".join(unique_words[:5])}',
            'current': ', '.join(unique_words),
            'suggestion': 'Replace with specific details and numbers',
        })
    
    return issues


def detect_buzzword_stuffing(text: str) -> List[Dict]:
    """
    Detect excessive buzzword usage.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of BUZZWORD_STUFFING issues
    """
    issues = []
    
    buzzword_count = 0
    found_buzzwords = []
    
    for buzzword in BUZZWORDS:
        pattern = re.compile(r'\b' + re.escape(buzzword) + r'\b', re.IGNORECASE)
        matches = pattern.findall(text)
        
        if matches:
            buzzword_count += len(matches)
            found_buzzwords.append(buzzword)
    
    if buzzword_count > BUZZWORD_THRESHOLD:
        issues.append({
            'issue_type': 'CONTENT_GENERIC_STATEMENTS',
            'location': 'Throughout CV',
            'description': f'Too many buzzwords ({buzzword_count} found): {", ".join(found_buzzwords[:5])}',
            'current': ', '.join(found_buzzwords[:10]),
            'suggestion': 'Replace buzzwords with specific achievements and results',
        })
    
    return issues


def detect_language_issues(text: str) -> List[Dict]:
    """
    Detect all language quality issues.
    
    This is the MAIN function for language analysis.
    100% deterministic - same text → same result.
    
    Args:
        text: Full CV text
        
    Returns:
        List of language issues
    """
    issues = []
    
    issues.extend(detect_weak_verbs(text))
    issues.extend(detect_vague_language(text))
    issues.extend(detect_buzzword_stuffing(text))
    
    return issues
