"""
CV length scoring category.
Max: 5 points
"""

from ..config import CATEGORY_WEIGHTS


def calculate_length_score(data) -> float:
    """
    Calculate CV length score.
    
    Scoring logic:
    - 1 page: 5 points (optimal for most cases)
    - 2 pages: 4 points (acceptable)
    - 3+ pages: 2 points (too long)
    - Less than 1 page: 1 point (too short)
    """
    # Handle both dict and dataclass
    if isinstance(data, dict):
        pages = data.get("page_count", 1)
    else:
        pages = data.page_count
    
    if pages == 1:
        return 5.0
    elif pages == 2:
        return 4.0
    elif pages >= 3:
        return 2.0
    else:
        return 1.0
