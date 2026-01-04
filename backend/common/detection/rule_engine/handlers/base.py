"""
Base Handler - abstract class for all detection handlers.

IMPORTANT: Uses CVStructure from section_extractor.py
"""

from abc import ABC, abstractmethod


class BaseHandler(ABC):
    """Abstract base class for detection handlers."""
    pass


class DetectedIssue:
    """Represents a detected issue."""
    pass
