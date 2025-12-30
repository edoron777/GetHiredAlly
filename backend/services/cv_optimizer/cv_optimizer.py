"""
CV Optimizer Service - Main integration module
Version: 4.0

Integrates AI data extraction with deterministic scoring.
"""

from typing import Dict, Any, Optional, Callable

from .cv_analyzer import extract_cv_data, get_empty_cv_data
from common.scoring import calculate_cv_score
from common.scoring.calculator import get_score_message, calculate_improvement


def analyze_cv(cv_text: str, call_ai_model: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Analyze CV and calculate deterministic score.
    
    Flow:
    1. AI extracts structured data
    2. Code calculates score from data
    3. Return score + breakdown + issues
    
    Args:
        cv_text: Raw CV text content
        call_ai_model: Function to call AI model for extraction
    
    Returns:
        Dictionary with score, breakdown, grade, and issues
    """
    extracted_data = extract_cv_data(cv_text, call_ai_model)
    
    score_result = calculate_cv_score(extracted_data)
    
    message = get_score_message(score_result.total_score)
    
    return {
        'score': score_result.total_score,
        'breakdown': score_result.breakdown,
        'grade': score_result.grade,
        'grade_label': score_result.grade_label,
        'message': message,
        'issues': extracted_data.get('issues', []),
        'issues_count': score_result.issues_count,
        'auto_fixable_count': score_result.auto_fixable_count,
        'extracted_data': extracted_data,
        'scoring_version': '4.0.0'
    }


def score_fixed_cv(
    original_cv: str, 
    fixed_cv: str, 
    call_ai_model: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Score the fixed CV using the SAME algorithm.
    
    CRITICAL: This ensures real improvement measurement.
    The fixed CV is re-analyzed and re-scored, not estimated.
    
    Args:
        original_cv: Original CV text
        fixed_cv: Fixed/improved CV text
        call_ai_model: Function to call AI model for extraction
    
    Returns:
        Dictionary with before/after scores and improvement metrics
    """
    original_data = extract_cv_data(original_cv, call_ai_model)
    original_result = calculate_cv_score(original_data)
    
    fixed_data = extract_cv_data(fixed_cv, call_ai_model)
    fixed_result = calculate_cv_score(fixed_data)
    
    improvement = calculate_improvement(
        original_result.total_score,
        fixed_result.total_score
    )
    
    return {
        'before_score': original_result.total_score,
        'after_score': fixed_result.total_score,
        'improvement_points': improvement['improvement_points'],
        'improvement_percent': improvement['improvement_percent'],
        'before_breakdown': original_result.breakdown,
        'after_breakdown': fixed_result.breakdown,
        'before_grade': original_result.grade_label,
        'after_grade': fixed_result.grade_label,
        'before_issues_count': original_result.issues_count,
        'after_issues_count': fixed_result.issues_count,
        'scoring_version': '4.0.0'
    }


def get_database_payload(score_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare payload for database storage.
    
    Args:
        score_result: Result from analyze_cv or score_fixed_cv
    
    Returns:
        Dictionary ready for database insertion
    """
    return {
        'score': score_result.get('score'),
        'score_breakdown': score_result.get('breakdown'),
        'scoring_version': score_result.get('scoring_version', '4.0.0'),
        'grade': score_result.get('grade'),
        'grade_label': score_result.get('grade_label'),
        'issues_count': score_result.get('issues_count', 0),
        'auto_fixable_count': score_result.get('auto_fixable_count', 0)
    }


def get_fixed_cv_database_payload(fixed_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare payload for fixed CV database storage.
    
    Args:
        fixed_result: Result from score_fixed_cv
    
    Returns:
        Dictionary ready for database update
    """
    return {
        'fixed_score': fixed_result.get('after_score'),
        'improvement_percent': fixed_result.get('improvement_percent'),
        'fixed_breakdown': fixed_result.get('after_breakdown'),
        'before_grade': fixed_result.get('before_grade'),
        'after_grade': fixed_result.get('after_grade'),
        'scoring_version': fixed_result.get('scoring_version', '4.0.0')
    }
