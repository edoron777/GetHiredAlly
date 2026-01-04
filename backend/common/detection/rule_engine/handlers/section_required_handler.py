"""
Section Required Handler

Detects when required sections are missing.

detection_config format:
{
    "type": "section_required",
    "section_name": "skills",
    "section_patterns": [
        "^\\s*skills?\\s*$",
        "^\\s*technical skills?\\s*$"
    ],
    "issue_when": "missing"
}
"""

import re
import logging
from typing import List

from .base import BaseHandler, DetectedIssue
from ...section_extractor import CVStructure
from ..cache import DetectionRule

logger = logging.getLogger(__name__)


class SectionRequiredHandler(BaseHandler):
    """
    Handler for required section detection.
    """
    
    def detect(
        self, 
        cv_text: str, 
        cv_structure: CVStructure, 
        rule: DetectionRule
    ) -> List[DetectedIssue]:
        """
        Detect missing required sections.
        """
        issues = []
        config = rule.detection_config
        
        section_name = config.get('section_name', '')
        section_patterns = config.get('section_patterns', [])
        issue_when = config.get('issue_when', 'missing')
        
        section_exists = self._check_cv_structure(cv_structure, section_name)
        
        if not section_exists and section_patterns:
            section_exists = self._check_patterns(cv_text, section_patterns)
        
        should_trigger = (
            (issue_when == 'missing' and not section_exists) or
            (issue_when == 'found' and section_exists)
        )
        
        if should_trigger:
            if issue_when == 'missing':
                match_text = f"No '{section_name}' section found"
            else:
                match_text = f"'{section_name}' section found"
            
            issue = self.create_issue(
                rule=rule,
                match_text=match_text,
                details={
                    'section_name': section_name,
                    'section_exists': section_exists
                }
            )
            issues.append(issue)
        
        return issues
    
    def _check_cv_structure(self, cv_structure: CVStructure, section_name: str) -> bool:
        """Check if section exists in CVStructure."""
        section_name_lower = section_name.lower()
        
        if section_name_lower == 'summary':
            return cv_structure.has_summary
        elif section_name_lower == 'experience':
            return cv_structure.has_experience
        elif section_name_lower == 'education':
            return cv_structure.has_education
        elif section_name_lower == 'skills':
            return cv_structure.has_skills
        
        for section in cv_structure.sections:
            if hasattr(section, 'name') and section_name_lower in section.name.lower():
                return True
        
        return False
    
    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if any pattern matches in text."""
        for pattern_str in patterns:
            try:
                pattern = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
                if pattern.search(text):
                    return True
            except re.error as e:
                logger.warning(f"Invalid section pattern: {e}")
        return False
