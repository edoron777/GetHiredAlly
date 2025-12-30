"""
CV length scoring category.
Max: 5 points (v3.0)
"""

def calculate_length_score(data: dict) -> float:
    """
    Calculate CV length score.
    
    Args:
        data: dict with page_count
        
    Returns:
        Score between 1 and 5
    """
    pages = data.get('page_count', 1)
    
    if pages == 1:
        return 5.0
    elif pages == 2:
        return 4.0
    elif pages == 3:
        return 2.0
    else:
        return 1.0
