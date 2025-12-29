"""
After-fix score calculation.
Calculates projected score based on fixability, NOT re-analysis.
"""

from typing import Dict, List
from .config import SCORE_MIN, SCORE_MAX, CATEGORY_WEIGHTS, FIXABILITY_RATES


def calculate_after_fix_score(
    before_score: int,
    issues: List[Dict],
    breakdown: Dict[str, float]
) -> Dict:
    """
    Calculate projected score after AI fixes are applied.
    
    This is an ESTIMATE, not a re-analysis.
    Based on which issues are auto-fixable.
    
    Args:
        before_score: Original CV score
        issues: List of detected issues
        breakdown: Score breakdown by category
        
    Returns:
        Dictionary with after_score, improvement, and details
    """
    
    # Group issues by category
    issues_by_category = {}
    for issue in issues:
        cat = issue.get("category", "other")
        if cat not in issues_by_category:
            issues_by_category[cat] = []
        issues_by_category[cat].append(issue)
    
    # Calculate recovery for each category
    recovery_points = 0.0
    category_improvements = {}
    
    for category, cat_issues in issues_by_category.items():
        fixability = FIXABILITY_RATES.get(category, 0.3)
        
        # Count auto-fixable issues
        auto_fixable = sum(1 for i in cat_issues if i.get("is_auto_fixable", False))
        total_in_cat = len(cat_issues)
        
        if total_in_cat > 0:
            # Estimate points lost to this category
            max_points = CATEGORY_WEIGHTS.get(category, 10)
            current_points = breakdown.get(category, 0)
            points_lost = max_points - current_points
            
            # Calculate recovery
            fix_ratio = auto_fixable / total_in_cat
            recoverable = points_lost * fixability * fix_ratio
            recovery_points += recoverable
            
            category_improvements[category] = {
                "before": round(current_points, 1),
                "after": round(current_points + recoverable, 1),
                "improvement": round(recoverable, 1)
            }
    
    # Calculate after score
    after_score = before_score + recovery_points
    
    # Apply bounds - NEVER 100%
    after_score = max(SCORE_MIN, min(SCORE_MAX, after_score))
    
    improvement = round(after_score - before_score)
    
    # Generate message
    if improvement >= 20:
        message = "Significant improvement! Your CV is much stronger now."
    elif improvement >= 10:
        message = "Nice improvement! Your CV is noticeably better."
    elif improvement > 0:
        message = "Your CV has been polished."
    else:
        message = "Some issues require manual improvement for best results."
    
    return {
        "before_score": before_score,
        "after_score": round(after_score),
        "improvement": improvement,
        "improvement_percentage": round((improvement / max(before_score, 1)) * 100),
        "message": message,
        "category_improvements": category_improvements,
        "max_possible": SCORE_MAX
    }
