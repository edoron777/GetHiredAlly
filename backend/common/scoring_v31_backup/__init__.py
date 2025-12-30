"""
CV Scoring Module v3.0
Deterministic scoring for CV/Resume analysis.

Usage:
    from backend.common.scoring import calculate_cv_score
    
    result = calculate_cv_score(extracted_data)
    print(f"Score: {result['total_score']}")
    print(f"Grade: {result['grade']}")
"""

from .calculator import calculate_cv_score
from .after_fix import calculate_after_fix_score

__all__ = [
    'calculate_cv_score',
    'calculate_after_fix_score'
]
