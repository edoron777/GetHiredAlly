"""
Static Detection Module for CV Optimizer

This module provides deterministic issue detection using static rules.
Same CV text → Same issues found → Same results ALWAYS
"""

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
