"""
Count Handler

Detects issues based on counting items (bullets, certifications, etc.)

detection_config format:
{
    "type": "count",
    "count_what": "bullets",
    "target_section": "experience",
    "min_count": 3,
    "max_count": 8,
    "issue_when": "outside_range"
}
"""

import re
import logging
from typing import List

from .base import BaseHandler, DetectedIssue
from ...section_extractor import CVStructure
from ..cache import DetectionRule

logger = logging.getLogger(__name__)


class CountHandler(BaseHandler):
    """
    Handler for count-based detection.
    """
    
    def detect(
        self, 
        cv_text: str, 
        cv_structure: CVStructure, 
        rule: DetectionRule
    ) -> List[DetectedIssue]:
        """
        Detect count-based issues.
        """
        issues = []
        config = rule.detection_config
        
        count_what = config.get('count_what', 'bullets')
        target_section = config.get('target_section', 'all')
        min_count = config.get('min_count')
        max_count = config.get('max_count')
        issue_when = config.get('issue_when', 'outside_range')
        
        text = self.get_target_text(cv_structure, target_section)
        if not text:
            return issues
        
        count = self._count_items(text, count_what)
        
        below_min = min_count is not None and count < min_count
        above_max = max_count is not None and count > max_count
        
        should_trigger = (
            (issue_when == 'below_min' and below_min) or
            (issue_when == 'above_max' and above_max) or
            (issue_when == 'outside_range' and (below_min or above_max))
        )
        
        if should_trigger:
            if below_min:
                match_text = f"Only {count} {count_what} found (minimum: {min_count})"
            else:
                match_text = f"{count} {count_what} found (maximum: {max_count})"
            
            issue = self.create_issue(
                rule=rule,
                match_text=match_text,
                location=target_section,
                details={
                    'count': count,
                    'count_what': count_what,
                    'min_count': min_count,
                    'max_count': max_count,
                    'target_section': target_section
                }
            )
            issues.append(issue)
        
        return issues
    
    def _count_items(self, text: str, count_what: str) -> int:
        """Count different types of items."""
        if count_what == 'bullets':
            pattern = r'^[\s]*[•\-\*\>\◦\▪]\s'
            return len(re.findall(pattern, text, re.MULTILINE))
        
        elif count_what == 'words':
            return len(text.split())
        
        elif count_what == 'lines':
            return len([l for l in text.split('\n') if l.strip()])
        
        elif count_what == 'certifications':
            cert_patterns = [
                r'\b(certified|certification|certificate|license)\b',
                r'\b(AWS|PMP|CPA|CFA|CISSP|CISA)\b',
            ]
            count = 0
            for pattern in cert_patterns:
                count += len(re.findall(pattern, text, re.IGNORECASE))
            return count
        
        elif count_what == 'numbers':
            return len(re.findall(r'\d+(?:\.\d+)?[%$KMB]?', text))
        
        else:
            return 0
