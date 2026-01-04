"""
CV Parser Package - Static (Non-AI) Resume Parser
Version: 1.0
"""

from .enhanced_parser import EnhancedCVParser
from .section_detector import detect_sections
from .skills_extractor import extract_skills

__all__ = ['EnhancedCVParser', 'detect_sections', 'extract_skills']
