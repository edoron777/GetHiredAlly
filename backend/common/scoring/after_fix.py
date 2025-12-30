"""
After-fix score calculation v3.1
Uses REAL scores from actual CV scoring, not predictions.
"""

from typing import Dict, List
from .config import CATEGORY_WEIGHTS

# Map AI category names to config category names
CATEGORY_MAP = {
    "Lack of Quantification": "quantification",
    "Weak Presentation": "language",
    "Formatting & Structure": "formatting",
    "Missing Information": "contact",
    "Spelling & Grammar": "grammar",
    "Grammar & Spelling": "grammar",
    "Skills": "skills",
    "Experience": "experience",
    "Length": "length",
    "Contact Information": "contact",
    "Tech-Specific": "skills",
    "Tailoring": "experience",
    "Career Narrative": "experience",
    "Employment Gaps": "experience",
    "Personal Information": "contact",
}


def normalize_category(category: str) -> str:
    """Normalize AI category name to config category name."""
    if category in CATEGORY_MAP:
        return CATEGORY_MAP[category]
    lower = category.lower()
    if lower in CATEGORY_WEIGHTS:
        return lower
    for key in CATEGORY_WEIGHTS:
        if key in lower:
            return key
    return "other"


def calculate_after_fix_score(
    before_score: int,
    after_score: int,
    issues: List[Dict]
) -> Dict:
    """
    Calculate improvement based on ACTUAL before and after scores.
    No more predictions - uses real scores from extract_cv_data_and_score().
    
    Args:
        before_score: Score of original CV (from extract_cv_data_and_score)
        after_score: Score of fixed CV (from extract_cv_data_and_score)
        issues: List of issues (for category tracking only)
    
    Returns:
        Dict with real scores and category improvements for display
    """
    # REAL improvement calculation
    improvement = after_score - before_score
    
    # Count issues by category (for "What Improved" display)
    category_counts = {}
    for issue in issues:
        cat = normalize_category(issue.get('category', 'other'))
        is_fixable = issue.get('is_auto_fixable', False)
        
        if cat not in category_counts:
            category_counts[cat] = {'total': 0, 'fixable': 0}
        
        category_counts[cat]['total'] += 1
        if is_fixable:
            category_counts[cat]['fixable'] += 1
    
    # Build category improvements for display
    category_improvements = {}
    total_issues_fixed = 0
    
    for cat, counts in category_counts.items():
        if counts['fixable'] > 0:
            total_issues_fixed += counts['fixable']
            max_points = CATEGORY_WEIGHTS.get(cat, 10)
            category_improvements[cat] = {
                'issues_fixed': counts['fixable'],
                'total_issues': counts['total'],
                'improvement': counts['fixable'],
                'max_possible': max_points,
                'before': 0,
                'after': counts['fixable']
            }
    
    # Generate message based on REAL improvement
    if improvement >= 15:
        message = "Excellent improvement! Your CV is now much stronger."
    elif improvement >= 8:
        message = "Great improvement! Your CV is noticeably better."
    elif improvement > 0:
        message = "Your CV has been improved and polished."
    else:
        message = "Some issues require your input for best results."
    
    return {
        'before_score': before_score,
        'after_score': after_score,
        'improvement': improvement,
        'message': message,
        'category_improvements': category_improvements,
        'total_issues_fixed': total_issues_fixed,
        'total_issues': sum(c['total'] for c in category_counts.values()),
    }
