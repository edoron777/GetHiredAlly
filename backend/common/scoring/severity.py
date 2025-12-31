"""
Severity Assignment Module

This module provides DETERMINISTIC severity assignment for CV issues.
Severity is assigned by CODE based on issue_type, NOT by AI.

RULE: Same issue_type → Same severity (ALWAYS)

Supports legacy issue types via LEGACY_ISSUE_TYPE_MAPPING.
"""

import logging
from typing import Dict, List, Any

from .config import (
    ISSUE_TYPE_CONFIG,
    LEGACY_ISSUE_TYPE_MAPPING,
    DEFAULT_SEVERITY,
    DEFAULT_UI_CATEGORY,
    VALID_SEVERITIES,
)

logger = logging.getLogger(__name__)


def normalize_issue_type(issue_type: str) -> str:
    """
    Normalize issue type, converting legacy types to new catalog types.
    
    Args:
        issue_type: Raw issue type string
        
    Returns:
        Normalized issue type (uppercase, mapped from legacy if needed)
    """
    if not issue_type:
        return ''
    
    normalized = issue_type.strip().upper()
    
    if normalized in LEGACY_ISSUE_TYPE_MAPPING:
        mapped = LEGACY_ISSUE_TYPE_MAPPING[normalized]
        logger.debug(f"Mapped legacy issue type '{normalized}' -> '{mapped}'")
        return mapped
    
    return normalized


def get_severity_for_issue_type(issue_type: str) -> str:
    """
    Get severity for an issue type from static configuration.
    
    Args:
        issue_type: The issue type identifier (e.g., 'SPELLING_ERROR' or 'GRAMMAR_SPELLING_ERROR')
        
    Returns:
        Severity level: 'critical', 'important', 'consider', or 'polish'
        
    Note:
        Supports legacy issue types via automatic mapping.
        Returns DEFAULT_SEVERITY ('consider') for unknown issue types.
    """
    if not issue_type:
        logger.warning("Empty issue_type received, using default severity")
        return DEFAULT_SEVERITY
    
    normalized_type = normalize_issue_type(issue_type)
    
    if normalized_type in ISSUE_TYPE_CONFIG:
        return ISSUE_TYPE_CONFIG[normalized_type]['severity']
    
    logger.warning(f"Unknown issue_type: '{issue_type}', using default severity '{DEFAULT_SEVERITY}'")
    return DEFAULT_SEVERITY


def get_ui_category_for_issue_type(issue_type: str) -> str:
    """
    Get UI category for an issue type from static configuration.
    
    Note: Uses 'category' field from new config structure.
    """
    if not issue_type:
        return DEFAULT_UI_CATEGORY
    
    normalized_type = normalize_issue_type(issue_type)
    
    if normalized_type in ISSUE_TYPE_CONFIG:
        return ISSUE_TYPE_CONFIG[normalized_type].get('category', DEFAULT_UI_CATEGORY)
    
    return DEFAULT_UI_CATEGORY


def get_display_name_for_issue_type(issue_type: str) -> str:
    """
    Get human-readable display name for an issue type.
    """
    if not issue_type:
        return "Unknown Issue"
    
    normalized_type = normalize_issue_type(issue_type)
    
    if normalized_type in ISSUE_TYPE_CONFIG:
        return ISSUE_TYPE_CONFIG[normalized_type]['display_name']
    
    return issue_type.replace('_', ' ').title()


def is_auto_fixable(issue_type: str) -> bool:
    """
    Check if an issue type can be auto-fixed by AI.
    """
    if not issue_type:
        return False
    
    normalized_type = normalize_issue_type(issue_type)
    
    if normalized_type in ISSUE_TYPE_CONFIG:
        return ISSUE_TYPE_CONFIG[normalized_type].get('auto_fixable', False)
    
    return False


def get_weight_for_issue_type(issue_type: str) -> int:
    """
    Get weight for an issue type from static configuration.
    
    Args:
        issue_type: The issue type identifier
        
    Returns:
        Weight value (1-10) for scoring purposes
    """
    if not issue_type:
        return 5
    
    normalized_type = normalize_issue_type(issue_type)
    
    if normalized_type in ISSUE_TYPE_CONFIG:
        return ISSUE_TYPE_CONFIG[normalized_type].get('weight', 5)
    
    return 5


def get_subcategory_for_issue_type(issue_type: str) -> str:
    """
    Get subcategory for an issue type from static configuration.
    """
    if not issue_type:
        return 'General'
    
    normalized_type = normalize_issue_type(issue_type)
    
    if normalized_type in ISSUE_TYPE_CONFIG:
        return ISSUE_TYPE_CONFIG[normalized_type].get('subcategory', 'General')
    
    return 'General'


def assign_severity_to_issues(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Assign severity to a list of issues based on their issue_type.
    
    This is the MAIN FUNCTION that should be called after detection/analysis.
    It ensures deterministic severity assignment for ALL issues.
    Supports legacy issue types via automatic mapping.
    
    Args:
        issues: List of issue dictionaries from detection
                Each issue should have 'issue_type' field
                
    Returns:
        List of issues with severity, category, and metadata fields added
        
    Example:
        Input:  [{'issue_type': 'SPELLING_ERROR', 'description': '...'}]
        Output: [{'issue_type': 'GRAMMAR_SPELLING_ERROR', 'description': '...', 
                  'severity': 'critical', 'category': 'Grammar & Language'}]
    """
    if not issues:
        return []
    
    processed_issues = []
    
    for issue in issues:
        processed_issue = issue.copy()
        
        issue_type = issue.get('issue_type', issue.get('type', ''))
        
        normalized_type = normalize_issue_type(issue_type)
        
        processed_issue['severity'] = get_severity_for_issue_type(issue_type)
        category = get_ui_category_for_issue_type(issue_type)
        processed_issue['category'] = category
        processed_issue['ui_category'] = category
        processed_issue['subcategory'] = get_subcategory_for_issue_type(issue_type)
        processed_issue['display_name'] = get_display_name_for_issue_type(issue_type)
        processed_issue['auto_fixable'] = is_auto_fixable(issue_type)
        processed_issue['weight'] = get_weight_for_issue_type(issue_type)
        
        if issue_type:
            processed_issue['issue_type'] = normalized_type
        
        processed_issues.append(processed_issue)
    
    return processed_issues


def count_issues_by_severity(issues: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Count issues by severity level.
    
    Args:
        issues: List of issues (must have 'severity' field)
        
    Returns:
        Dictionary with counts: {'critical': N, 'important': N, 'consider': N, 'polish': N}
    """
    counts = {severity: 0 for severity in VALID_SEVERITIES}
    
    for issue in issues:
        severity = issue.get('severity', DEFAULT_SEVERITY)
        if severity in counts:
            counts[severity] += 1
        else:
            counts[DEFAULT_SEVERITY] += 1
    
    return counts
