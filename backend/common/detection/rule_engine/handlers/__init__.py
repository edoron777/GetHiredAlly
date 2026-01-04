"""
Detection Handlers
"""

from .base import BaseHandler, DetectedIssue
from .regex_handler import RegexHandler

__all__ = ['BaseHandler', 'DetectedIssue', 'RegexHandler']
