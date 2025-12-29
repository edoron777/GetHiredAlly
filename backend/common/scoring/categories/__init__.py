"""
Category scoring functions.
Each function takes ExtractedData and returns a score.
"""

from .grammar import calculate_grammar_score
from .formatting import calculate_formatting_score
from .quantification import calculate_quantification_score
from .language import calculate_language_score
from .contact import calculate_contact_score
from .skills import calculate_skills_score
from .experience import calculate_experience_score
from .length import calculate_length_score

__all__ = [
    'calculate_grammar_score',
    'calculate_formatting_score',
    'calculate_quantification_score',
    'calculate_language_score',
    'calculate_contact_score',
    'calculate_skills_score',
    'calculate_experience_score',
    'calculate_length_score'
]
