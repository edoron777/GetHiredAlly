"""
Static Detection Module for CV Optimizer

This module provides deterministic issue detection using static rules.
Same CV text → Same issues found → Same results ALWAYS
"""

from .master_detector import detect_all_issues, get_detection_summary
from .contact_extractor import extract_contact_info
from .section_extractor import extract_sections
from .bullet_extractor import extract_bullets
from .word_lists import (
    WEAK_VERBS,
    STRONG_VERBS,
    BUZZWORDS,
    BUZZWORD_THRESHOLD,
    VAGUE_WORDS,
    VAGUE_THRESHOLD,
    FILLER_PHRASES,
    SUMMARY_HEADERS,
    EXPERIENCE_HEADERS,
    EDUCATION_HEADERS,
    SKILLS_HEADERS,
    MONTH_NAMES,
    CURRENT_INDICATORS,
)
