"""
Formatting & Structure Scoring (18 points)
- Visual Structure: 6 points
- Section Organization: 5 points
- Consistency: 3 points
- ATS Compatibility: 4 points

DETERMINISTIC: Same input = Same score.
"""

from typing import Dict, Any
from ..config import FORMATTING_WEIGHTS


def score_formatting(extracted_data: Dict[str, Any]) -> float:
    """
    Calculate Formatting & Structure score (max 18 points).
    
    DETERMINISTIC: Same extracted_data = Same score.
    """
    score = 0.0
    
    score += _score_visual_structure(extracted_data)
    score += _score_section_organization(extracted_data)
    score += _score_consistency(extracted_data)
    score += _score_ats_compatibility(extracted_data)
    
    return max(0, min(18, score))


def _score_visual_structure(data: Dict[str, Any]) -> float:
    """Score visual structure (max 6 points)."""
    max_points = FORMATTING_WEIGHTS['visual_structure']
    score = 0.0
    
    structure = data.get('structure', {})
    
    # Has section headers (2 points)
    if structure.get('has_section_headers', False):
        score += 2.0
    
    # Uses bullet points (1.5 points)
    if structure.get('uses_bullet_points', False):
        score += 1.5
    
    # Adequate whitespace (1 point)
    if structure.get('has_adequate_whitespace', True):
        score += 1.0
    
    # Clear visual hierarchy (1.5 points)
    if structure.get('has_clear_hierarchy', True):
        score += 1.5
    
    return min(max_points, score)


def _score_section_organization(data: Dict[str, Any]) -> float:
    """Score section organization (max 5 points)."""
    max_points = FORMATTING_WEIGHTS['section_organization']
    score = 0.0
    
    structure = data.get('structure', {})
    
    # Contact at top (1.5 points)
    if structure.get('contact_at_top', True):
        score += 1.5
    
    # Experience prominent (1.5 points)
    if structure.get('experience_prominent', True):
        score += 1.5
    
    # Logical section order (1 point)
    if structure.get('logical_order', True):
        score += 1.0
    
    # Education positioned correctly (1 point)
    if structure.get('education_positioned', True):
        score += 1.0
    
    return min(max_points, score)


def _score_consistency(data: Dict[str, Any]) -> float:
    """Score consistency (max 3 points)."""
    max_points = FORMATTING_WEIGHTS['consistency']
    score = max_points  # Start with full, deduct for issues
    
    formatting = data.get('formatting', {})
    
    # Inconsistent bullet style (-1)
    if not formatting.get('consistent_bullets', True):
        score -= 1.0
    
    # Inconsistent date format (-1)
    if not formatting.get('consistent_dates', True):
        score -= 1.0
    
    # Inconsistent spacing (-1)
    if not formatting.get('consistent_spacing', True):
        score -= 1.0
    
    return max(0, score)


def _score_ats_compatibility(data: Dict[str, Any]) -> float:
    """Score ATS compatibility (max 4 points)."""
    max_points = FORMATTING_WEIGHTS['ats_compatibility']
    score = max_points  # Start with full, deduct for issues
    
    ats = data.get('ats', {})
    
    # Has tables (-0.5)
    if ats.get('has_tables', False):
        score -= 0.5
    
    # Has text boxes (-0.5)
    if ats.get('has_text_boxes', False):
        score -= 0.5
    
    # Has images (-0.3)
    if ats.get('has_images', False):
        score -= 0.3
    
    # Multi-column layout (-0.5)
    if ats.get('is_multi_column', False):
        score -= 0.5
    
    # Non-standard section names (-0.5)
    if not ats.get('standard_section_names', True):
        score -= 0.5
    
    # Non-parseable dates (-0.3)
    if not ats.get('parseable_dates', True):
        score -= 0.3
    
    return max(0, score)
