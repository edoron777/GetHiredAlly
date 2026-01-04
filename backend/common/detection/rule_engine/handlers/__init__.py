"""
Detection Handlers
"""

from .base import BaseHandler, DetectedIssue
from .regex_handler import RegexHandler
from .word_list_handler import WordListHandler

__all__ = ['BaseHandler', 'DetectedIssue', 'RegexHandler', 'WordListHandler']
