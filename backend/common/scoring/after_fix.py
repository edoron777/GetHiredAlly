"""
After-fix score calculation v3.0
Projects score improvement based on fixable issues.
"""

from typing import Dict, List
from .config import SCORE_MAX, FIXABILITY_RATES, CATEGORY_WEIGHTS


def calculate_after_fix_score(
    before_score: int,
    issues: List[Dict],
    breakdown: Dict[str, float]
) -> Dict:
    """
    Calculate projected score after fixes.
    
    Args:
        before_score: Original CV score
        issues: List of detected issues
        breakdown: Score breakdown by category
        
    Returns:
        Dictionary with before/after scores and improvements
    """
    recovery_points = 0.0
    category_improvements = {}
    
    # Group issues by category
    issues_by_category = {}
    for issue in issues:
        cat = issue.get("category", "other")
        if cat not in issues_by_category:
            issues_by_category[cat] = []
        issues_by_category[cat].append(issue)
    
    # Calculate recovery for each category
    for category, cat_issues in issues_by_category.items():
        if category not in FIXABILITY_RATES:
            continue
            
        fixability = FIXABILITY_RATES[category]
        max_points = CATEGORY_WEIGHTS.get(category, 10)
        current_points = breakdown.get(category, 0)
        points_lost = max_points - current_points
        
        # Count auto-fixable issues
        auto_fixable = sum(1 for i in cat_issues if i.get("is_auto_fixable", False))
        total_in_cat = len(cat_issues)
        
        if total_in_cat > 0:
            fix_ratio = auto_fixable / total_in_cat
            recoverable = points_lost * fixability * fix_ratio
            recovery_points += recoverable
            
            category_improvements[category] = {
                "before": round(current_points, 1),
                "after": round(min(max_points, current_points + recoverable), 1),
                "improvement": round(recoverable, 1),
                "max_possible": max_points
            }
    
    # Calculate after score (capped at 95)
    after_score = min(SCORE_MAX, before_score + recovery_points)
    improvement = round(after_score - before_score)
    
    # Generate message
    if improvement >= 15:
        message = "Significant improvement! Your CV will be much stronger."
    elif improvement >= 8:
        message = "Nice improvement! Your CV will be noticeably better."
    elif improvement > 0:
        message = "Your CV has been polished."
    else:
        message = "Some issues require your input for best results."
    
    return {
        "before_score": before_score,
        "after_score": round(after_score),
        "improvement": improvement,
        "message": message,
        "category_improvements": category_improvements,
        "max_possible": SCORE_MAX
    }
