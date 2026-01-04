"""
Detection Handlers

Each handler implements one detection type.
All handlers use CVStructure from section_extractor.py
"""

from .base import BaseHandler, DetectedIssue

__all__ = ['BaseHandler', 'DetectedIssue']
