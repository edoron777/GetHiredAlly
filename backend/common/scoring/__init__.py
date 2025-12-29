"""
CV Scoring Module
Reusable, deterministic scoring for CV/Resume analysis.

Usage:
    from common.scoring import calculate_cv_score, ScoreResult
    
    result = calculate_cv_score(extracted_data)
    print(f"Score: {result.total_score}")
    print(f"Grade: {result.grade}")
"""

from .calculator import calculate_cv_score
from .after_fix import calculate_after_fix_score
from .models import ScoreResult, ScoreBreakdown, ExtractedData, IssueCategory, IssueSeverity
from .config import SCORING_VERSION, SCORE_MIN, SCORE_MAX, CATEGORY_WEIGHTS

__all__ = [
    'calculate_cv_score',
    'calculate_after_fix_score',
    'ScoreResult',
    'ScoreBreakdown',
    'ExtractedData',
    'IssueCategory',
    'IssueSeverity',
    'SCORING_VERSION',
    'SCORE_MIN',
    'SCORE_MAX',
    'CATEGORY_WEIGHTS'
]
