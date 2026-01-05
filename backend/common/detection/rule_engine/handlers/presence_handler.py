"""
Presence Handler

Detects issues when required patterns are missing OR present.

detection_config format:
{
    "type": "presence",
    "patterns": ["[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"],
    "target_section": "contact",
    "require_any": true,
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


class PresenceHandler(BaseHandler):
    """
    Handler for presence/absence detection.
    
    Checks if required patterns are present or missing.
    """
    
    def detect(
        self, 
        cv_text: str, 
        cv_structure: CVStructure, 
        rule: DetectionRule
    ) -> List[DetectedIssue]:
        """
        Detect presence or absence of patterns.
        """
        skip_codes = ['CONTENT_MISSING_IMPACT', 'CONTENT_MISSING_METRICS']
        if hasattr(rule, 'issue_code') and rule.issue_code in skip_codes:
            return []
        
        issues = []
        config = rule.detection_config
        
        if not self.validate_config(rule, ['patterns']):
            return issues
        
        patterns = config.get('patterns', [])
        target_section = config.get('target_section', 'all')
        require_any = config.get('require_any', True)
        issue_when = config.get('issue_when', 'missing')
        
        if not patterns:
            return issues
        
        text = self.get_target_text(cv_structure, target_section)
        
        print(f"[PresenceHandler] {rule.issue_code}")
        print(f"  target_section: {target_section}")
        print(f"  text length: {len(text) if text else 0}")
        print(f"  text preview: {text[:200] if text else 'EMPTY'}...")
        print(f"  patterns: {patterns}")
        
        if not text:
            print(f"  ERROR: Section '{target_section}' is EMPTY!")
            if issue_when == 'missing':
                issue = self.create_issue(
                    rule=rule,
                    current='',
                    description=f"Section '{target_section}' is empty or not found",
                    location=target_section,
                    is_highlightable=False
                )
                issues.append(issue)
            return issues
        
        flags_str = config.get('flags', 'i')
        flags = 0
        if 'i' in flags_str.lower():
            flags |= re.IGNORECASE
        if 'm' in flags_str.lower():
            flags |= re.MULTILINE
        
        pattern_results = {}
        for pattern_str in patterns:
            try:
                pattern = re.compile(pattern_str, flags)
                match = pattern.search(text)
                pattern_results[pattern_str] = match is not None
                print(f"  pattern '{pattern_str[:50]}': {'FOUND' if match else 'NOT FOUND'}")
                if match:
                    print(f"    matched: '{match.group()}'")
            except re.error as e:
                logger.warning(f"Invalid pattern in {rule.issue_code}: {e}")
                pattern_results[pattern_str] = False
                print(f"  pattern ERROR: {e}")
        
        if require_any:
            patterns_found = any(pattern_results.values())
        else:
            patterns_found = all(pattern_results.values())
        
        should_trigger = (
            (issue_when == 'missing' and not patterns_found) or
            (issue_when == 'found' and patterns_found)
        )
        
        if should_trigger:
            if issue_when == 'missing':
                section_preview = text[:150] if text else "Section not found"
                current_text = f"Not found in: {section_preview}..."
            else:
                current_text = ''
            
            issue = self.create_issue(
                rule=rule,
                current=current_text,
                location=target_section,
                is_highlightable=False,
                details={
                    'pattern_results': pattern_results,
                    'issue_when': issue_when,
                    'target_section': target_section
                }
            )
            issues.append(issue)
        
        return issues
