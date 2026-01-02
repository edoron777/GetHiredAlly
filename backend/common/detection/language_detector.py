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

FIRST_PERSON_PATTERN = re.compile(r"\b(I|my|me|myself|I'm|I've|I'll)\b")

PASSIVE_VOICE_PATTERNS = [
    re.compile(r'\b(was|were|been|being)\s+\w+ed\b', re.IGNORECASE),
    re.compile(r'\bwas\s+(assigned|given|told|asked|tasked|made|selected)\b', re.IGNORECASE),
    re.compile(r'\b(is|are|was|were)\s+being\s+\w+ed\b', re.IGNORECASE),
]

VAGUE_METRICS_PATTERNS = [
    re.compile(r'\b(significantly|greatly|substantially)\s+(increased|improved|reduced)', re.IGNORECASE),
    re.compile(r'\b(many|several|numerous|various|multiple)\s+(projects?|clients?|customers?|tasks?)', re.IGNORECASE),
    re.compile(r'\b(a lot of|tons of|lots of)\b', re.IGNORECASE),
    re.compile(r'\b(some|few|couple)\s+(of\s+)?(projects?|tasks?)', re.IGNORECASE),
]

IRRELEVANT_INFO_PATTERNS = {
    'high_school': re.compile(r'\b(high school|secondary school|secondary education)\b', re.IGNORECASE),
    'personal_info': re.compile(r'\b(blood type|horoscope|zodiac|marital status|married|single|divorced|spouse|children)\b', re.IGNORECASE),
    'age_dob': re.compile(r'\b(age|born|date of birth|DOB|birthdate)\s*:?\s*\d', re.IGNORECASE),
    'religion': re.compile(r'\b(religion|religious affiliation)\s*:', re.IGNORECASE),
    'nationality': re.compile(r'\b(nationality|citizen of|passport number)\b', re.IGNORECASE),
}


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
                    current_text = match.strip()
                    issues.append({
                        'issue_type': 'CONTENT_WEAK_ACTION_VERBS',
                        'title': f"Weak action verb: '{verb}'",
                        'location': 'Experience Section',
                        'description': f'Weak/passive phrase detected: "{verb}"',
                        'current': current_text,
                        'is_highlightable': bool(current_text and current_text in text),
                        'weak_verb': verb,
                        'suggestion': f"Replace '{verb}' with stronger verb: led, achieved, delivered, implemented",
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
        first_word = unique_words[0] if unique_words else ''
        
        current_text = ''
        if first_word:
            pattern = re.compile(r'\b' + re.escape(first_word) + r'\b', re.IGNORECASE)
            match = pattern.search(text)
            if match:
                line_start = text.rfind('\n', 0, match.start()) + 1
                line_end = text.find('\n', match.start())
                if line_end == -1:
                    line_end = len(text)
                current_text = text[line_start:line_end].strip()
        
        issues.append({
            'issue_type': 'CONTENT_GENERIC_STATEMENTS',
            'title': 'Vague language detected',
            'location': 'Throughout CV',
            'description': f'Too many vague words ({vague_count} found): {", ".join(unique_words[:5])}',
            'current': current_text if current_text else first_word,
            'is_highlightable': bool(current_text),
            'count': vague_count,
            'all_instances': unique_words[:10],
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
        first_buzzword = found_buzzwords[0] if found_buzzwords else ''
        
        current_text = ''
        if first_buzzword:
            pattern = re.compile(r'\b' + re.escape(first_buzzword) + r'\b', re.IGNORECASE)
            match = pattern.search(text)
            if match:
                line_start = text.rfind('\n', 0, match.start()) + 1
                line_end = text.find('\n', match.start())
                if line_end == -1:
                    line_end = len(text)
                current_text = text[line_start:line_end].strip()
        
        issues.append({
            'issue_type': 'CONTENT_BUZZWORD_STUFFING',
            'title': 'Excessive buzzwords',
            'location': 'Throughout CV',
            'description': f'Too many buzzwords ({buzzword_count} found): {", ".join(found_buzzwords[:5])}',
            'current': current_text if current_text else first_buzzword,
            'is_highlightable': bool(current_text),
            'count': buzzword_count,
            'all_instances': found_buzzwords[:10],
            'suggestion': 'Replace buzzwords with specific achievements and results',
        })
    
    return issues


def detect_first_person_pronouns(text: str) -> List[Dict]:
    """
    Detect excessive use of first-person pronouns.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of CONTENT_FIRST_PERSON_PRONOUNS issues
    """
    issues = []
    
    matches = list(FIRST_PERSON_PATTERN.finditer(text))
    
    if len(matches) > 3:
        first_match = matches[0]
        start = first_match.start()
        
        line_start = text.rfind('\n', 0, start) + 1
        line_end = text.find('\n', start)
        if line_end == -1:
            line_end = len(text)
        
        first_sentence = text[line_start:line_end].strip()
        
        all_instances = []
        for match in matches[:5]:
            ls = text.rfind('\n', 0, match.start()) + 1
            le = text.find('\n', match.start())
            if le == -1:
                le = len(text)
            line_text = text[ls:le].strip()
            if line_text and line_text not in all_instances:
                all_instances.append(line_text)
        
        issues.append({
            'issue_type': 'CONTENT_FIRST_PERSON_PRONOUNS',
            'location': 'Throughout CV',
            'description': f'Excessive first-person pronouns ({len(matches)} found): I, my, me, etc.',
            'current': first_sentence,
            'is_highlightable': bool(first_sentence and first_sentence in text),
            'count': len(matches),
            'all_instances': all_instances[:5],
            'suggestion': 'CVs should be written without "I" statements (e.g., "Led team" not "I led team")',
        })
    
    return issues


def detect_passive_voice(text: str) -> List[Dict]:
    """
    Detect passive voice constructions.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of CONTENT_PASSIVE_VOICE issues
    """
    issues = []
    passive_matches = []
    
    for pattern in PASSIVE_VOICE_PATTERNS:
        for match in pattern.finditer(text):
            passive_matches.append(match)
    
    if len(passive_matches) > 5:
        first_match = passive_matches[0]
        
        line_start = text.rfind('\n', 0, first_match.start()) + 1
        line_end = text.find('\n', first_match.start())
        if line_end == -1:
            line_end = len(text)
        first_sentence = text[line_start:line_end].strip()
        
        all_instances = []
        for match in passive_matches[:5]:
            ls = text.rfind('\n', 0, match.start()) + 1
            le = text.find('\n', match.start())
            if le == -1:
                le = len(text)
            line_text = text[ls:le].strip()
            if line_text and line_text not in all_instances:
                all_instances.append(line_text)
        
        issues.append({
            'issue_type': 'CONTENT_PASSIVE_VOICE',
            'title': 'Passive voice detected',
            'location': 'Throughout CV',
            'description': f'Passive voice detected ({len(passive_matches)} instances)',
            'current': first_sentence,
            'is_highlightable': bool(first_sentence and first_sentence in text),
            'count': len(passive_matches),
            'all_instances': all_instances[:5],
            'suggestion': 'Use active voice: "Managed team" instead of "Was assigned to manage team"',
        })
    
    return issues


def detect_vague_metrics(text: str) -> List[Dict]:
    """
    Detect vague quantifiers instead of specific numbers.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of CONTENT_VAGUE_METRICS issues
    """
    issues = []
    vague_matches = []
    
    for pattern in VAGUE_METRICS_PATTERNS:
        for match in pattern.finditer(text):
            vague_matches.append(match)
    
    if len(vague_matches) > 3:
        first_match = vague_matches[0]
        
        line_start = text.rfind('\n', 0, first_match.start()) + 1
        line_end = text.find('\n', first_match.start())
        if line_end == -1:
            line_end = len(text)
        first_sentence = text[line_start:line_end].strip()
        
        all_instances = []
        for match in vague_matches[:5]:
            ls = text.rfind('\n', 0, match.start()) + 1
            le = text.find('\n', match.start())
            if le == -1:
                le = len(text)
            line_text = text[ls:le].strip()
            if line_text and line_text not in all_instances:
                all_instances.append(line_text)
        
        issues.append({
            'issue_type': 'CONTENT_VAGUE_METRICS',
            'title': 'Vague metrics detected',
            'location': 'Throughout CV',
            'description': f'Vague quantifiers used instead of specific numbers ({len(vague_matches)} found)',
            'current': first_sentence,
            'is_highlightable': bool(first_sentence and first_sentence in text),
            'count': len(vague_matches),
            'all_instances': all_instances[:5],
            'suggestion': 'Replace with specific numbers: "significantly increased" → "increased by 35%"',
        })
    
    return issues


def detect_irrelevant_information(text: str, has_college_degree: bool = False) -> List[Dict]:
    """
    Detect information that shouldn't be on a CV.
    
    Args:
        text: Text to analyze
        has_college_degree: Whether CV mentions college education
        
    Returns:
        List of CONTENT_IRRELEVANT_INFORMATION issues
    """
    issues = []
    found_issues = []
    
    college_pattern = re.compile(r'\b(bachelor|master|phd|doctorate|university|college|degree)\b', re.IGNORECASE)
    has_college = bool(college_pattern.search(text))
    
    for info_type, pattern in IRRELEVANT_INFO_PATTERNS.items():
        if info_type == 'high_school' and not has_college:
            continue
        
        match = pattern.search(text)
        if match:
            found_issues.append(info_type.replace('_', ' '))
    
    if found_issues:
        first_match_text = ''
        for info_type, pattern in IRRELEVANT_INFO_PATTERNS.items():
            match = pattern.search(text)
            if match:
                first_match_text = match.group()
                break
        
        issues.append({
            'issue_type': 'CONTENT_IRRELEVANT_INFORMATION',
            'title': 'Irrelevant information found',
            'location': 'Throughout CV',
            'description': f'Potentially irrelevant information found: {", ".join(found_issues)}',
            'current': first_match_text,
            'is_highlightable': bool(first_match_text and first_match_text in text),
            'all_instances': found_issues,
            'suggestion': 'Remove personal details not relevant to job qualifications',
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
    issues.extend(detect_first_person_pronouns(text))
    issues.extend(detect_passive_voice(text))
    issues.extend(detect_vague_metrics(text))
    issues.extend(detect_irrelevant_information(text))
    
    return issues
