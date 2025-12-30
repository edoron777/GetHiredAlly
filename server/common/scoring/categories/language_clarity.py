"""
Language & Clarity Scoring (18 points)
- Grammar & Spelling: 8 points
- Writing Quality: 5 points
- Vagueness Detection: 5 points

DETERMINISTIC: Same input = Same score.
"""

from typing import Dict, Any
from ..config import (
    LANGUAGE_CLARITY_WEIGHTS,
    REDUNDANT_PHRASES,
    FILLER_WORDS,
    VAGUE_PHRASES
)


def score_language_clarity(extracted_data: Dict[str, Any]) -> float:
    """
    Calculate Language & Clarity score (max 18 points).
    
    DETERMINISTIC: Same extracted_data = Same score.
    """
    score = 0.0
    
    # 1. Grammar & Spelling (8 points)
    score += _score_grammar_spelling(extracted_data)
    
    # 2. Writing Quality (5 points)
    score += _score_writing_quality(extracted_data)
    
    # 3. Vagueness Detection (5 points)
    score += _score_vagueness(extracted_data)
    
    return max(0, min(18, score))


def _score_grammar_spelling(data: Dict[str, Any]) -> float:
    """
    Score grammar and spelling (max 8 points).
    
    Penalty-based: start with max, deduct for errors.
    """
    max_points = LANGUAGE_CLARITY_WEIGHTS['grammar_spelling']
    
    grammar = data.get('grammar', {})
    spelling_errors = grammar.get('spelling_errors_count', 0)
    grammar_errors = grammar.get('grammar_errors_count', 0)
    
    total_errors = spelling_errors + grammar_errors
    
    # Penalty: 1.5 points per error
    penalty = total_errors * 1.5
    
    return max(0, max_points - penalty)


def _score_writing_quality(data: Dict[str, Any]) -> float:
    """
    Score writing quality (max 5 points).
    
    Checks: redundant phrases, filler words, sentence length.
    """
    max_points = LANGUAGE_CLARITY_WEIGHTS['writing_quality']
    score = max_points
    
    writing = data.get('writing_quality', {})
    
    # Redundant phrases found (-0.5 each, max -1.5)
    redundant_count = writing.get('redundant_phrases_count', 0)
    score -= min(1.5, redundant_count * 0.5)
    
    # Filler words found (-0.3 each, max -1.5)
    filler_count = writing.get('filler_words_count', 0)
    score -= min(1.5, filler_count * 0.3)
    
    # Average sentence too long (-1 if > 25 words avg)
    avg_sentence_length = writing.get('avg_sentence_length', 15)
    if avg_sentence_length > 25:
        score -= 1.0
    elif avg_sentence_length > 20:
        score -= 0.5
    
    return max(0, score)


def _score_vagueness(data: Dict[str, Any]) -> float:
    """
    Score vagueness detection (max 5 points).
    
    Penalizes vague claims, rewards specific achievements.
    """
    max_points = LANGUAGE_CLARITY_WEIGHTS['vagueness']
    score = max_points
    
    vagueness = data.get('vagueness', {})
    
    # Vague phrases found (-0.5 each, max -2)
    vague_count = vagueness.get('vague_phrases_count', 0)
    score -= min(2.0, vague_count * 0.5)
    
    # Buzzword stuffing (-1 if > 5 buzzwords)
    buzzword_count = vagueness.get('buzzword_count', 0)
    if buzzword_count > 5:
        score -= 1.0
    
    # No specific achievements mentioned (-1)
    if not vagueness.get('has_specific_achievements', True):
        score -= 1.0
    
    return max(0, score)
