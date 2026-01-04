"""
Word List Handler

Detects issues by checking if words from a list appear in CV text.

detection_config format:
{
    "type": "word_list",
    "words": ["assisted", "helped", "worked on"],
    "match_location": "line_start",
    "target_section": "experience",
    "case_sensitive": false,
    "min_matches": 1
}
"""

import re
import logging
from typing import List

from .base import BaseHandler, DetectedIssue
from ...section_extractor import CVStructure
from ..cache import DetectionRule

logger = logging.getLogger(__name__)


class WordListHandler(BaseHandler):
    """
    Handler for word list-based detection.
    
    Checks if words/phrases from a list appear in CV text.
    """
    
    def detect(
        self, 
        cv_text: str, 
        cv_structure: CVStructure, 
        rule: DetectionRule
    ) -> List[DetectedIssue]:
        """
        Detect words/phrases from list.
        """
        issues = []
        config = rule.detection_config
        
        if not self.validate_config(rule, ['words']):
            return issues
        
        words = config.get('words', [])
        match_location = config.get('match_location', 'anywhere')
        target_section = config.get('target_section', 'all')
        case_sensitive = config.get('case_sensitive', False)
        min_matches = config.get('min_matches', 1)
        
        if not words:
            return issues
        
        text = self.get_target_text(cv_structure, target_section)
        if not text:
            return issues
        
        found_words = []
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for word in words:
            escaped_word = re.escape(word)
            
            if match_location == 'line_start':
                pattern = rf'^[\s•\-\*]*{escaped_word}\b'
            elif match_location == 'line_end':
                pattern = rf'\b{escaped_word}\s*$'
            else:
                pattern = rf'\b{escaped_word}\b'
            
            try:
                matches = re.findall(pattern, text, flags | re.MULTILINE)
                if matches:
                    found_words.extend(matches)
            except re.error as e:
                logger.warning(f"Invalid pattern for word '{word}': {e}")
        
        if len(found_words) >= min_matches:
            unique_found = list(set(w.strip().lower() for w in found_words))
            first_match = found_words[0].strip() if found_words else ''
            description = f"{len(found_words)} found: {', '.join(unique_found[:10])}"
            
            issue = self.create_issue(
                rule=rule,
                current=first_match,
                description=description,
                location=target_section,
                is_highlightable=bool(first_match and first_match in text),
                details={
                    'found_words': unique_found,
                    'total_matches': len(found_words),
                    'target_section': target_section
                }
            )
            issues.append(issue)
        
        return issues
