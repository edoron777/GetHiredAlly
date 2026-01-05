"""
Language Quality Detector

Detects weak verbs, vague descriptions, and buzzword stuffing.
100% CODE - No AI - Deterministic results.

SECTION-AWARE: Weak verbs and buzzwords only checked in Experience section.
"""

import re
from typing import List, Dict
from .word_lists import (
    WEAK_VERBS,
    STRONG_VERBS,
    BUZZWORDS,
    VAGUE_WORDS,
    BUZZWORD_THRESHOLD,
    VAGUE_THRESHOLD,
)
from .section_extractor import extract_sections

MIN_WEAK_VERBS_FOR_ISSUE = 3  # Need 3+ different weak verbs to trigger
WEAK_VERB_RATIO_THRESHOLD = 0.30  # 30% - if weak verbs are 30%+ of total action verbs

FIRST_PERSON_PATTERN = re.compile(r"\b(I|my|me|myself|I'm|I've|I'll)\b")


def get_experience_text_only(text: str) -> str:
    """
    Extract ONLY the Experience/Work section text.
    This excludes: Summary, Education, Certifications, Skills
    """
    try:
        structure = extract_sections(text)
        if structure and structure.experience:
            return structure.experience
        else:
            experience_markers = [
                'work experience', 'professional experience', 
                'employment history', 'career history',
                'experience'
            ]
            text_lower = text.lower()
            
            for marker in experience_markers:
                start_idx = text_lower.find(marker)
                if start_idx != -1:
                    section_headers = [
                        'education', 'certifications', 'skills',
                        'projects', 'awards', 'publications',
                        'references', 'languages'
                    ]
                    end_idx = len(text)
                    for header in section_headers:
                        header_idx = text_lower.find(header, start_idx + len(marker))
                        if header_idx != -1 and header_idx < end_idx:
                            end_idx = header_idx
                    
                    return text[start_idx:end_idx]
            
            return text
    except Exception:
        return text


def is_certification_line(line: str) -> bool:
    """
    Check if a line is likely a certification name.
    Certification lines should NOT be checked for weak verbs.
    """
    cert_indicators = [
        'certified', 'certificate', 'certification',
        '(aws)', '(gcp)', '(azure)', '(ibm)', '(google)',
        'professional', 'associate', 'specialist',
        'coursera', 'udemy', 'linkedin learning',
        'skillup', 'deeplearning.ai'
    ]
    line_lower = line.lower()
    return any(indicator in line_lower for indicator in cert_indicators)

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
    Detect weak action verbs in experience section.
    Only triggers if weak verbs are a significant pattern, not isolated cases.
    
    SECTION-AWARE: Only checks Experience section, skips certifications.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of WEAK_ACTION_VERBS issues (max 1 consolidated issue)
    """
    issues = []
    
    experience_text = get_experience_text_only(text)
    
    weak_verbs_found = set()
    weak_verb_examples = []
    
    for line in experience_text.split('\n'):
        line = line.strip()
        
        if not line:
            continue
        
        if is_certification_line(line):
            continue
        
        line_lower = line.lower()
        
        for verb in WEAK_VERBS:
            if verb.lower() in line_lower:
                if verb not in weak_verbs_found:
                    weak_verbs_found.add(verb)
                    weak_verb_examples.append({
                        'verb': verb,
                        'line': line[:100]
                    })
    
    strong_verbs_count = 0
    for line in experience_text.split('\n'):
        line_lower = line.lower().strip()
        for verb in STRONG_VERBS:
            if line_lower.startswith(verb.lower()):
                strong_verbs_count += 1
                break
    
    total_verbs = len(weak_verbs_found) + strong_verbs_count
    weak_ratio = len(weak_verbs_found) / total_verbs if total_verbs > 0 else 0
    
    should_trigger = (
        len(weak_verbs_found) >= MIN_WEAK_VERBS_FOR_ISSUE or
        (weak_ratio >= WEAK_VERB_RATIO_THRESHOLD and len(weak_verbs_found) >= 2)
    )
    
    if should_trigger:
        weak_list = sorted(list(weak_verbs_found))[:5]
        
        issues.append({
            'issue_type': 'CONTENT_WEAK_ACTION_VERBS',
            'title': 'Multiple weak action verbs found',
            'location': 'Experience Section',
            'description': f'Found {len(weak_verbs_found)} weak/passive verbs: {", ".join(weak_list)}. Replace with strong action verbs.',
            'current': ', '.join(weak_list),
            'is_highlightable': False,
            'weak_verbs': list(weak_verbs_found),
            'weak_verb_count': len(weak_verbs_found),
            'examples': weak_verb_examples[:3],
            'suggestion': 'Replace weak verbs with powerful action verbs: Led, Developed, Achieved, Implemented, Increased, Reduced, Created, Built.',
        })
    
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
    
    SECTION-AWARE: Only checks Experience section bullets, not Summary.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of BUZZWORD_STUFFING issues
    """
    issues = []
    
    experience_text = get_experience_text_only(text)
    
    buzzword_count = 0
    found_buzzwords = []
    
    for buzzword in BUZZWORDS:
        pattern = re.compile(r'\b' + re.escape(buzzword) + r'\b', re.IGNORECASE)
        matches = pattern.findall(experience_text)
        
        if matches:
            buzzword_count += len(matches)
            found_buzzwords.append(buzzword)
    
    if buzzword_count > BUZZWORD_THRESHOLD:
        first_buzzword = found_buzzwords[0] if found_buzzwords else ''
        
        current_text = ''
        if first_buzzword:
            pattern = re.compile(r'\b' + re.escape(first_buzzword) + r'\b', re.IGNORECASE)
            match = pattern.search(experience_text)
            if match:
                line_start = experience_text.rfind('\n', 0, match.start()) + 1
                line_end = experience_text.find('\n', match.start())
                if line_end == -1:
                    line_end = len(experience_text)
                current_text = experience_text[line_start:line_end].strip()
        
        issues.append({
            'issue_type': 'CONTENT_BUZZWORD_STUFFING',
            'title': 'Excessive buzzwords',
            'location': 'Experience Section',
            'description': f'Too many buzzwords ({buzzword_count} found): {", ".join(found_buzzwords[:5])}',
            'current': current_text if current_text else first_buzzword,
            'is_highlightable': bool(current_text and current_text in text),
            'count': buzzword_count,
            'all_instances': found_buzzwords[:10],
            'suggestion': f'This section has {buzzword_count} buzzwords (like "leveraging", "innovative", "cutting-edge"). Recruiters prefer specific achievements. Instead of "leveraged innovative solutions", try "Reduced costs by 30% using automated testing".',
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
            'suggestion': f'Your CV uses first-person words ({len(matches)} found: I, my, me). Professional CVs are stronger without them. Instead of "I managed a team", write "Managed a team of 5 engineers".',
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
            'suggestion': 'This sentence uses passive voice. Active voice is more powerful. Instead of "The project was completed by me", write "Completed the project ahead of schedule".',
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
