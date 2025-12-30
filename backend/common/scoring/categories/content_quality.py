"""
Content Quality Scoring (40 points)
- Quantification: 20 points
- Action Verbs: 8 points
- Career Narrative: 6 points
- Content Depth: 6 points

DETERMINISTIC: Same input = Same score.
"""

from typing import Dict, Any
from ..config import (
    CONTENT_QUALITY_WEIGHTS,
    STRONG_VERBS,
    WEAK_VERBS
)
from ..extractors.pattern_matcher import PatternMatcher


def score_content_quality(extracted_data: Dict[str, Any]) -> float:
    """
    Calculate Content Quality score (max 40 points).
    
    DETERMINISTIC: Same extracted_data = Same score.
    """
    score = 0.0
    
    # 1. Quantification (20 points)
    score += _score_quantification(extracted_data)
    
    # 2. Action Verbs (8 points)
    score += _score_action_verbs(extracted_data)
    
    # 3. Career Narrative (6 points)
    score += _score_career_narrative(extracted_data)
    
    # 4. Content Depth (6 points)
    score += _score_content_depth(extracted_data)
    
    # Ensure bounds
    return max(0, min(40, score))


def _score_quantification(data: Dict[str, Any]) -> float:
    """
    Score quantified achievements (max 20 points).
    
    Checks for: percentages, dollar amounts, team sizes, 
    time metrics, project counts, user numbers.
    """
    max_points = CONTENT_QUALITY_WEIGHTS['quantification']
    
    quant = data.get('quantification', {})
    total_bullets = quant.get('total_bullet_points', 0)
    quantified = quant.get('bullets_with_numbers', 0)
    
    if total_bullets == 0:
        return 0
    
    ratio = quantified / total_bullets
    
    # Scoring table based on quantification ratio
    if ratio >= 0.80:
        return max_points  # 20
    elif ratio >= 0.60:
        return max_points * 0.80  # 16
    elif ratio >= 0.40:
        return max_points * 0.60  # 12
    elif ratio >= 0.20:
        return max_points * 0.40  # 8
    elif ratio >= 0.10:
        return max_points * 0.20  # 4
    else:
        return 0


def _score_action_verbs(data: Dict[str, Any]) -> float:
    """
    Score action verb usage (max 8 points).
    
    Rewards strong verbs, penalizes weak verbs.
    """
    max_points = CONTENT_QUALITY_WEIGHTS['action_verbs']
    
    lang = data.get('language', {})
    strong_count = lang.get('strong_action_verbs_count', 0)
    weak_count = lang.get('weak_phrases_count', 0)
    total_bullets = data.get('quantification', {}).get('total_bullet_points', 1)
    
    if total_bullets == 0:
        total_bullets = 1
    
    # Calculate strong verb ratio
    strong_ratio = strong_count / total_bullets
    
    # Base score from strong verb ratio
    if strong_ratio >= 0.80:
        score = max_points  # 8
    elif strong_ratio >= 0.60:
        score = max_points * 0.80  # 6.4
    elif strong_ratio >= 0.40:
        score = max_points * 0.60  # 4.8
    elif strong_ratio >= 0.20:
        score = max_points * 0.40  # 3.2
    else:
        score = max_points * 0.20  # 1.6
    
    # Penalty for weak verbs (0.5 points each, max 2 point penalty)
    weak_penalty = min(2.0, weak_count * 0.5)
    score -= weak_penalty
    
    return max(0, score)


def _score_career_narrative(data: Dict[str, Any]) -> float:
    """
    Score career narrative quality (max 6 points).
    
    Checks: summary section, appropriate length, chronological order.
    """
    max_points = CONTENT_QUALITY_WEIGHTS['career_narrative']
    score = 0.0
    
    structure = data.get('structure', {})
    experience = data.get('experience', {})
    
    # Has professional summary (2 points)
    if structure.get('has_summary_section', False):
        score += 2.0
        
        # Summary length appropriate - 50-150 words (1 point)
        summary_words = structure.get('summary_word_count', 0)
        if 50 <= summary_words <= 150:
            score += 1.0
        elif 30 <= summary_words <= 200:
            score += 0.5
    
    # Reverse chronological order (1.5 points)
    if experience.get('is_reverse_chronological', False):
        score += 1.5
    
    # Clear job titles (1.5 points)
    if experience.get('has_clear_titles', False):
        score += 1.5
    
    return min(max_points, score)


def _score_content_depth(data: Dict[str, Any]) -> float:
    """
    Score content depth (max 6 points).
    
    Checks: description length, bullet count, consistency across jobs.
    """
    max_points = CONTENT_QUALITY_WEIGHTS['content_depth']
    score = max_points  # Start with full, deduct for issues
    
    experience = data.get('experience', {})
    jobs = experience.get('jobs', [])
    
    if not jobs:
        # If no jobs data, use simpler check
        word_count = data.get('structure', {}).get('word_count', 0)
        if word_count < 200:
            return 2.0
        elif word_count < 400:
            return 4.0
        return max_points
    
    word_counts = []
    
    for job in jobs:
        words = job.get('word_count', 0)
        bullets = job.get('bullet_count', 0)
        word_counts.append(words)
        
        # Too short description (-1 point each, max -2)
        if words < 30:
            score -= 1.0
        
        # Too few bullets (-0.5 each, max -1)
        if bullets < 3:
            score -= 0.5
    
    # Check for uneven detail across jobs
    if len(word_counts) >= 2:
        avg = sum(word_counts) / len(word_counts)
        if avg > 0:
            variance = max(word_counts) - min(word_counts)
            if variance / avg > 0.5:
                score -= 1.0
    
    return max(0, min(max_points, score))
