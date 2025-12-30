"""
Main CV Score Calculator - DETERMINISTIC
Version: 4.0

CRITICAL: Same input MUST produce same output EVERY TIME.
No randomness, no AI interpretation in scoring.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from .config import (
    CATEGORY_WEIGHTS,
    SCORE_MIN,
    SCORE_MAX,
    GRADE_THRESHOLDS
)
from .categories import (
    score_content_quality,
    score_language_clarity,
    score_formatting,
    score_completeness,
    score_professional,
    score_red_flags
)


@dataclass
class ScoreResult:
    """Result of CV score calculation."""
    total_score: int
    breakdown: Dict[str, float]
    grade: str
    grade_label: str
    issues_count: int
    auto_fixable_count: int


def calculate_cv_score(extracted_data: Dict[str, Any]) -> ScoreResult:
    """
    Calculate CV score from extracted data.
    
    DETERMINISTIC: Same input = Same output, ALWAYS.
    
    Args:
        extracted_data: Dictionary containing structured CV data
                       (from AI extraction or pattern matching)
    
    Returns:
        ScoreResult with total score, breakdown, and grade
    """
    breakdown = {}
    
    # Calculate each category score
    breakdown['content_quality'] = score_content_quality(extracted_data)
    breakdown['language_clarity'] = score_language_clarity(extracted_data)
    breakdown['formatting'] = score_formatting(extracted_data)
    breakdown['completeness'] = score_completeness(extracted_data)
    breakdown['professional'] = score_professional(extracted_data)
    breakdown['red_flags'] = score_red_flags(extracted_data)
    
    # Calculate total (sum of all categories)
    total = sum(breakdown.values())
    
    # Apply bounds
    total = max(SCORE_MIN, min(SCORE_MAX, total))
    
    # Get grade
    grade, grade_label = get_grade(total)
    
    # Count issues
    issues = extracted_data.get('issues', [])
    issues_count = len(issues)
    auto_fixable_count = sum(1 for i in issues if i.get('is_auto_fixable', False))
    
    return ScoreResult(
        total_score=round(total),
        breakdown={k: round(v, 1) for k, v in breakdown.items()},
        grade=grade,
        grade_label=grade_label,
        issues_count=issues_count,
        auto_fixable_count=auto_fixable_count
    )


def get_grade(score: float) -> tuple:
    """
    Convert numeric score to grade.
    
    Returns:
        Tuple of (grade_key, grade_label)
    """
    if score >= GRADE_THRESHOLDS['excellent']:
        return ('excellent', 'Excellent')
    elif score >= GRADE_THRESHOLDS['good']:
        return ('good', 'Good')
    elif score >= GRADE_THRESHOLDS['fair']:
        return ('fair', 'Fair')
    elif score >= GRADE_THRESHOLDS['needs_work']:
        return ('needs_work', 'Needs Work')
    else:
        return ('poor', 'Poor')


def get_score_message(score: int) -> str:
    """
    Get user-friendly message for score.
    
    Args:
        score: Total CV score (0-100)
    
    Returns:
        Encouraging message appropriate for score level
    """
    if score >= 90:
        return "Outstanding! Your CV is highly polished and job-ready."
    elif score >= 80:
        return "Great CV! Minor polish will make it perfect."
    elif score >= 70:
        return "Good foundation! A few improvements will help you stand out."
    elif score >= 60:
        return "Decent CV. Several improvements recommended."
    elif score >= 50:
        return "Your CV needs attention in multiple areas."
    else:
        return "Significant improvements needed. Focus on critical issues first."


def calculate_improvement(before_score: int, after_score: int) -> Dict[str, Any]:
    """
    Calculate improvement between before and after scores.
    
    Args:
        before_score: Original CV score
        after_score: Fixed CV score
    
    Returns:
        Dictionary with improvement details
    """
    improvement = after_score - before_score
    improvement_percent = round((improvement / max(before_score, 1)) * 100)
    
    return {
        'before_score': before_score,
        'after_score': after_score,
        'improvement_points': improvement,
        'improvement_percent': improvement_percent
    }
