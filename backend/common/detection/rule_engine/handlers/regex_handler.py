"""
Regex Handler

Detects issues using regular expression pattern matching.

detection_config format:
{
    "type": "regex",
    "pattern": "\\b(I|my|me)\\b",
    "flags": "gi",
    "target_section": "all",
    "min_matches": 3,
    "max_matches": null,
    "return_matches": true
}
"""

import re
import logging
from typing import List

from .base import BaseHandler, DetectedIssue
from ...section_extractor import CVStructure
from ..cache import DetectionRule

logger = logging.getLogger(__name__)


class RegexHandler(BaseHandler):
    """
    Handler for regex-based detection.
    
    Matches a pattern against CV text and triggers issue based on match count.
    """
    
    def detect(
        self, 
        cv_text: str, 
        cv_structure: CVStructure, 
        rule: DetectionRule
    ) -> List[DetectedIssue]:
        """
        Detect regex pattern matches.
        
        Triggers issue if:
        - min_matches is set and count >= min_matches
        - max_matches is set and count > max_matches
        """
        issues = []
        config = rule.detection_config
        
        if not self.validate_config(rule, ['pattern']):
            return issues
        
        pattern_str = config.get('pattern')
        flags_str = config.get('flags', 'i')
        target_section = config.get('target_section', 'all')
        min_matches = config.get('min_matches')
        max_matches = config.get('max_matches')
        return_matches = config.get('return_matches', True)
        
        logger.info(f"[DEBUG REGEX] Rule: {rule.issue_code}")
        logger.info(f"[DEBUG REGEX] target_section from config: {target_section}")
        logger.info(f"[DEBUG REGEX] pattern: {pattern_str}")
        
        flags = 0
        if 'i' in flags_str.lower():
            flags |= re.IGNORECASE
        if 'm' in flags_str.lower():
            flags |= re.MULTILINE
        
        text = self.get_target_text(cv_structure, target_section)
        logger.info(f"[DEBUG REGEX] text length from get_target_text: {len(text) if text else 0}")
        if text:
            logger.info(f"[DEBUG REGEX] text first 300 chars: {text[:300]}")
        
        if not text:
            logger.info(f"[DEBUG REGEX] NO TEXT - returning empty (target_section '{target_section}' not found)")
            return issues
        
        try:
            pattern = re.compile(pattern_str, flags)
            matches = pattern.findall(text)
            match_count = len(matches)
        except re.error as e:
            logger.error(f"Invalid regex pattern in {rule.issue_code}: {e}")
            return issues
        
        should_trigger = False
        
        if min_matches is not None and match_count >= min_matches:
            should_trigger = True
        
        if max_matches is not None and match_count > max_matches:
            should_trigger = True
        
        if should_trigger:
            if return_matches and matches:
                unique_matches = list(set(str(m) for m in matches[:10]))
                first_match = str(matches[0]) if matches else ''
                description = f"{match_count} found: {', '.join(unique_matches[:5])}"
            else:
                first_match = ''
                description = f"{match_count} matches found"
            
            if first_match.strip() == '':
                if '\n' in first_match or first_match == '':
                    current_display = '[blank line]'
                else:
                    current_display = '[whitespace]'
                is_highlight = False
            else:
                current_display = first_match[:47] + '...' if len(first_match) > 50 else first_match
                is_highlight = bool(current_display and current_display in text)
            
            issue = self.create_issue(
                rule=rule,
                current=current_display,
                description=description,
                location=target_section,
                is_highlightable=is_highlight,
                details={
                    'match_count': match_count,
                    'matches': [str(m)[:50] for m in matches[:20]] if return_matches else [],
                    'target_section': target_section
                }
            )
            issues.append(issue)
        
        return issues
