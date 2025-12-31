"""
AI Enhancement Module

Enhances CODE-detected issues with AI-generated suggestions.
AI does NOT detect issues - only provides suggestions for existing issues.

RULE: Issue count is FIXED by CODE. AI only adds suggestions.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# DEPRECATED: SUGGESTION_TEMPLATES
# 
# These templates have been moved to the database (cv_issue_types.static_tip).
# The CatalogService now provides all suggestions via enrich_detected_issue().
# 
# Kept here for backward compatibility/fallback if catalog is unavailable.
# New code should use: catalog_service.enrich_detected_issue()
# 
# Date deprecated: 2025-12-31
# ═══════════════════════════════════════════════════════════════════════════

SUGGESTION_TEMPLATES = {
    'SPELLING_ERROR': 'Check spelling and correct "{current}" to proper spelling',
    'GRAMMAR_ERROR': 'Review grammar and fix the error',
    'MISSING_EMAIL': 'Add a professional email address (e.g., firstname.lastname@gmail.com)',
    'MISSING_PHONE': 'Add a phone number with country code if applying internationally',
    'MISSING_LINKEDIN': 'Add your LinkedIn profile URL to increase professional visibility',
    'INVALID_EMAIL': 'Correct the email format to a valid email address',
    'INVALID_PHONE': 'Correct the phone number format',
    'NO_METRICS': 'Add specific numbers, percentages, or dollar amounts to quantify your achievement',
    'WEAK_ACTION_VERBS': 'Replace with strong verbs like: led, achieved, delivered, increased, reduced',
    'VAGUE_DESCRIPTION': 'Replace vague words with specific details and measurable outcomes',
    'BUZZWORD_STUFFING': 'Replace buzzwords with concrete achievements and specific results',
    'WEAK_SUMMARY': 'Write a compelling 3-4 sentence summary highlighting your key qualifications',
    'SECTION_ORDER': 'Move Experience section before Education for non-students',
    'CV_TOO_LONG': 'Focus on recent, relevant experience and remove outdated information',
    'CV_TOO_SHORT': 'Add more detail to your experience and achievements',
    'BULLET_TOO_LONG': 'Split into multiple focused bullets or condense key points',
    'BULLET_TOO_SHORT': 'Add more detail about the achievement and its impact',
    'BULLET_FORMAT': 'Start bullet with a strong action verb (e.g., Led, Achieved, Developed)',
    'FORMAT_INCONSISTENT': 'Use consistent formatting throughout the document',
    'DATE_FORMAT_INCONSISTENT': 'Use one date format throughout (e.g., "Jan 2020" or "January 2020")',
    'WHITESPACE_ISSUE': 'Remove extra blank lines and ensure consistent spacing',
    'MINOR_FORMAT': 'Clean up formatting for a more professional appearance',
    'OUTDATED_INFO': 'Consider removing experience older than 10-15 years',
    'HEADER_STYLE': 'Use consistent capitalization for all section headers',
    'REPETITIVE_CONTENT': 'Vary your language to avoid repeating the same phrases',
}


def add_basic_suggestions(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add template-based suggestions to issues.
    
    This is fast and deterministic - no AI call needed.
    
    Args:
        issues: List of issues from static detection
        
    Returns:
        Same issues with 'suggestion' field added/enhanced
    """
    for issue in issues:
        issue_type = issue.get('issue_type', '')
        
        if 'suggestion' not in issue or not issue['suggestion']:
            template = SUGGESTION_TEMPLATES.get(issue_type, 'Review and improve this section')
            
            if '{current}' in template and 'current' in issue:
                suggestion = template.format(current=issue['current'])
            else:
                suggestion = template
            
            issue['suggestion'] = suggestion
    
    return issues


async def enhance_with_ai(
    issues: List[Dict[str, Any]],
    cv_text: str,
    ai_client: Any = None,
    max_enhancements: int = 5
) -> List[Dict[str, Any]]:
    """
    Optionally enhance top issues with AI-generated suggestions.
    
    AI does NOT:
    - Add new issues
    - Remove issues
    - Change issue counts
    - Decide what's wrong
    
    AI ONLY:
    - Provides better suggestions for existing issues
    - Generates rewrite examples
    
    Args:
        issues: List of issues from static detection
        cv_text: Full CV text for context
        ai_client: AI client for generating suggestions
        max_enhancements: Maximum issues to enhance with AI
        
    Returns:
        Same issues with enhanced suggestions (count unchanged)
    """
    original_count = len(issues)
    
    issues = add_basic_suggestions(issues)
    
    if not ai_client:
        logger.info("No AI client - using template suggestions only")
        return issues
    
    high_priority = [i for i in issues if i.get('severity') in ['critical', 'high']][:max_enhancements]
    
    if not high_priority:
        return issues
    
    logger.info(f"AI enhancement skipped (using template suggestions)")
    
    assert len(issues) == original_count, "AI enhancement must not change issue count"
    
    return issues
