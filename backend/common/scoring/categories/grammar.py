"""
Grammar scoring category.
Max: 10 points (v3.0)
Pass/fail hygiene - not a differentiator.
"""

def calculate_grammar_score(data: dict) -> float:
    """
    Calculate grammar and spelling score.
    
    Args:
        data: dict with grammar_errors_count and spelling_errors_count
        
    Returns:
        Score between 0 and 10
    """
    grammar_errors = data.get('grammar_errors_count', 0)
    spelling_errors = data.get('spelling_errors_count', 0)
    total_errors = grammar_errors + spelling_errors
    
    if total_errors == 0:
        return 10.0
    elif total_errors <= 2:
        return 8.0
    elif total_errors <= 5:
        return 5.0
    elif total_errors <= 8:
        return 2.0
    else:
        return 0.0
