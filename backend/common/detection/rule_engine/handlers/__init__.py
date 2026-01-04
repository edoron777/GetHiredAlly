"""
Detection Handlers

Each handler implements one detection type:
- regex: Pattern matching
- word_list: Check words from list
- presence: Must contain pattern
- absence: Must NOT contain pattern
- count: Count items
- length: Min/max length
- consistency: Same format
- section_required: Section must exist
- composite: Multiple checks combined

All handlers use CVStructure from section_extractor.py
"""

from .base import BaseHandler, DetectedIssue

__all__ = ['BaseHandler', 'DetectedIssue']
