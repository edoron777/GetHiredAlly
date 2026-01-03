"""
Length-Based Content Detector
=============================
Issues Detected:
- CONTENT_SUMMARY_TOO_LONG
- CONTENT_JOB_DESCRIPTION_TOO_SHORT
- CONTENT_JOB_DESCRIPTION_TOO_LONG
- CONTENT_EDUCATION_DESCRIPTION_TOO_SHORT

Version: 1.0 | Created: January 3, 2026
"""

import re
from typing import List, Dict
from .word_lists import (
    SUMMARY_MAX_WORDS,
    SUMMARY_MAX_SENTENCES,
    JOB_DESCRIPTION_MIN_BULLETS,
    JOB_DESCRIPTION_MAX_BULLETS,
    JOB_DESCRIPTION_MIN_WORDS,
    JOB_DESCRIPTION_MAX_WORDS,
    EDUCATION_MIN_WORDS,
    EDUCATION_EXPERIENCE_THRESHOLD
)


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def count_sentences(text: str) -> int:
    """Count sentences in text."""
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])


def detect_summary_too_long(summary_text: str) -> List[Dict]:
    """Detect if Professional Summary is too long."""
    issues = []
    
    if not summary_text or not summary_text.strip():
        return issues
    
    word_count = count_words(summary_text)
    sentence_count = count_sentences(summary_text)
    
    if word_count > SUMMARY_MAX_WORDS or sentence_count > SUMMARY_MAX_SENTENCES:
        issues.append({
            'issue_type': 'CONTENT_SUMMARY_TOO_LONG',
            'severity': 'consider',
            'location': 'Professional Summary',
            'details': f'{word_count} words, {sentence_count} sentences. Max: {SUMMARY_MAX_WORDS} words, {SUMMARY_MAX_SENTENCES} sentences.'
        })
    
    return issues


def detect_job_description_too_short(experience_entries: List[Dict]) -> List[Dict]:
    """Detect if any job description is too brief."""
    issues = []
    
    for entry in experience_entries:
        company = entry.get('company', 'Unknown Company')
        title = entry.get('title', '')
        bullets = entry.get('bullets', [])
        
        bullet_count = len(bullets)
        total_words = sum(count_words(b) for b in bullets)
        
        if bullet_count < JOB_DESCRIPTION_MIN_BULLETS or total_words < JOB_DESCRIPTION_MIN_WORDS:
            location = f"{title} at {company}" if title else company
            issues.append({
                'issue_type': 'CONTENT_JOB_DESCRIPTION_TOO_SHORT',
                'severity': 'important',
                'location': location,
                'details': f'{bullet_count} bullets, {total_words} words. Min: {JOB_DESCRIPTION_MIN_BULLETS} bullets, {JOB_DESCRIPTION_MIN_WORDS} words.'
            })
    
    return issues


def detect_job_description_too_long(experience_entries: List[Dict]) -> List[Dict]:
    """Detect if any job description is too lengthy."""
    issues = []
    
    for entry in experience_entries:
        company = entry.get('company', 'Unknown Company')
        title = entry.get('title', '')
        bullets = entry.get('bullets', [])
        
        bullet_count = len(bullets)
        total_words = sum(count_words(b) for b in bullets)
        
        if bullet_count > JOB_DESCRIPTION_MAX_BULLETS or total_words > JOB_DESCRIPTION_MAX_WORDS:
            location = f"{title} at {company}" if title else company
            issues.append({
                'issue_type': 'CONTENT_JOB_DESCRIPTION_TOO_LONG',
                'severity': 'consider',
                'location': location,
                'details': f'{bullet_count} bullets, {total_words} words. Max: {JOB_DESCRIPTION_MAX_BULLETS} bullets, {JOB_DESCRIPTION_MAX_WORDS} words.'
            })
    
    return issues


def detect_education_description_too_short(
    education_entries: List[Dict],
    years_experience: int = 0
) -> List[Dict]:
    """Detect if education entry lacks detail (for recent graduates)."""
    issues = []
    
    if years_experience >= EDUCATION_EXPERIENCE_THRESHOLD:
        return issues
    
    for entry in education_entries:
        institution = entry.get('institution', 'Unknown Institution')
        degree = entry.get('degree', '')
        description = entry.get('description', '')
        
        description_words = count_words(description) if description else 0
        
        if description_words < EDUCATION_MIN_WORDS:
            location = f"{degree} at {institution}" if degree else institution
            issues.append({
                'issue_type': 'CONTENT_EDUCATION_DESCRIPTION_TOO_SHORT',
                'severity': 'consider',
                'location': location,
                'details': f'Only {description_words} words. Add coursework, projects, or honors.'
            })
    
    return issues


def detect_all_length_issues(
    summary_text: str = '',
    experience_entries: List[Dict] = None,
    education_entries: List[Dict] = None,
    years_experience: int = 0
) -> List[Dict]:
    """Run all length-based detections."""
    issues = []
    
    if summary_text:
        issues.extend(detect_summary_too_long(summary_text))
    
    if experience_entries:
        issues.extend(detect_job_description_too_short(experience_entries))
        issues.extend(detect_job_description_too_long(experience_entries))
    
    if education_entries:
        issues.extend(detect_education_description_too_short(
            education_entries, 
            years_experience
        ))
    
    return issues
