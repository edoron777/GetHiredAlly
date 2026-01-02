"""
Static Detection Module for CV Optimizer

This module provides deterministic issue detection using static rules.
Same CV text → Same issues found → Same results ALWAYS
"""

from .master_detector import detect_all_issues, get_detection_summary
from .contact_extractor import extract_contact_info
from .section_extractor import extract_sections
from .bullet_extractor import extract_bullets
from .ai_enhancer import add_basic_suggestions, enhance_with_ai
from .fix_validator import validate_fix, restore_critical_elements, extract_critical_elements
from .standards_detector import detect_standards_issues
from .keywords_detector import detect_keywords_issues
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
