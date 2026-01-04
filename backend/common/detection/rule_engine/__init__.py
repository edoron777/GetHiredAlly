"""
Rule Engine Module

Database-driven detection system for CV analysis.
Reads detection rules from cv_issue_types.detection_config
and applies them to CV text.

REUSES:
- CVStructure from section_extractor.py (DO NOT recreate)
- CatalogService pattern from common/catalog/ (follow same structure)

Author: GetHiredAlly
Version: 1.0
Date: January 2026
"""

from .engine import RuleEngine
from .loader import RuleLoader, DetectionRule

__all__ = ['RuleEngine', 'RuleLoader', 'DetectionRule']
