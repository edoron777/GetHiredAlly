"""
Grammar scoring category.
Max: 15 points
"""

from ..config import CATEGORY_WEIGHTS


def calculate_grammar_score(data) -> float:
    """
    Calculate grammar and spelling score.
    
    Scoring logic:
    - 0 errors: 15 points (full score)
    - 1-2 errors: 12-13.5 points
    - 3-5 errors: 9-11.4 points
    - 6-10 errors: 5-10 points
    - 11+ errors: 0 points
    """
    max_points = CATEGORY_WEIGHTS["grammar"]
    
    # Handle both dict and dataclass
    if isinstance(data, dict):
        grammar_errors = data.get("grammar_errors_count", 0)
        spelling_errors = data.get("spelling_errors_count", 0)
    else:
        grammar_errors = data.grammar_errors_count
        spelling_errors = data.spelling_errors_count
    
    total_errors = grammar_errors + spelling_errors
    
    if total_errors == 0:
        return float(max_points)
    elif total_errors <= 2:
        return max_points - (total_errors * 1.5)
    elif total_errors <= 5:
        return max_points - (total_errors * 1.2)
    elif total_errors <= 10:
        return max(0.0, max_points - (total_errors * 1.0))
    else:
        return 0.0
