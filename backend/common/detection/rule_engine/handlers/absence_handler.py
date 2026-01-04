"""
Absence Handler

Detects issues when unwanted patterns ARE found (like tables).

detection_config format:
{
    "type": "absence",
    "patterns": ["^[^\\n]*\\|[^\\n]*\\|[^\\n]*$"],
    "target_section": "all",
    "consecutive_lines": 2,
    "issue_when": "found"
}
"""

import re
import logging
from typing import List

from .base import BaseHandler, DetectedIssue
from ...section_extractor import CVStructure
from ..cache import DetectionRule

logger = logging.getLogger(__name__)


class AbsenceHandler(BaseHandler):
    """
    Handler for detecting unwanted patterns.
    
    Commonly used for tables, special characters, etc.
    """
    
    def detect(
        self, 
        cv_text: str, 
        cv_structure: CVStructure, 
        rule: DetectionRule
    ) -> List[DetectedIssue]:
        """
        Detect unwanted patterns.
        """
        issues = []
        config = rule.detection_config
        
        if not self.validate_config(rule, ['patterns']):
            return issues
        
        patterns = config.get('patterns', [])
        target_section = config.get('target_section', 'all')
        consecutive_lines = config.get('consecutive_lines', 1)
        issue_when = config.get('issue_when', 'found')
        
        if not patterns:
            return issues
        
        text = self.get_target_text(cv_structure, target_section)
        if not text:
            return issues
        
        found_matches = []
        
        for pattern_str in patterns:
            try:
                if consecutive_lines > 1:
                    lines = text.split('\n')
                    consecutive_count = 0
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                    
                    for line in lines:
                        if pattern.search(line):
                            consecutive_count += 1
                            if consecutive_count >= consecutive_lines:
                                found_matches.append(f"Table-like structure ({consecutive_count} lines)")
                                break
                        else:
                            consecutive_count = 0
                else:
                    pattern = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
                    matches = pattern.findall(text)
                    if matches:
                        found_matches.extend(matches[:5])
                        
            except re.error as e:
                logger.warning(f"Invalid pattern in {rule.issue_code}: {e}")
        
        patterns_found = len(found_matches) > 0
        should_trigger = (
            (issue_when == 'found' and patterns_found) or
            (issue_when == 'none_found' and not patterns_found)
        )
        
        if should_trigger:
            if issue_when == 'found':
                match_text = f"Detected: {', '.join(str(m) for m in found_matches[:5])}"
            else:
                match_text = "Expected patterns not found"
            
            issue = self.create_issue(
                rule=rule,
                match_text=match_text,
                location=target_section,
                details={
                    'found_matches': found_matches[:10],
                    'target_section': target_section
                }
            )
            issues.append(issue)
        
        return issues
