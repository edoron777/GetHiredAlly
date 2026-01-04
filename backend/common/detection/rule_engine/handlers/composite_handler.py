"""
Composite Handler

Combines multiple detection checks with AND/OR logic.

detection_config format:
{
    "type": "composite",
    "logic": "and",
    "conditions": [
        {
            "type": "presence",
            "patterns": ["linkedin"],
            "target_section": "contact",
            "issue_when": "found"
        },
        {
            "type": "absence",
            "patterns": ["linkedin\\.com/in/"],
            "target_section": "contact",
            "issue_when": "found"
        }
    ],
    "issue_when": "all_match"
}
"""

import logging
from typing import List, TYPE_CHECKING

from .base import BaseHandler, DetectedIssue
from ...section_extractor import CVStructure
from ..cache import DetectionRule

if TYPE_CHECKING:
    from ..engine import RuleEngine

logger = logging.getLogger(__name__)


class CompositeHandler(BaseHandler):
    """
    Handler for composite (multi-condition) detection.
    
    Requires reference to RuleEngine to access other handlers.
    """
    
    def __init__(self, engine: 'RuleEngine' = None):
        """
        Initialize with reference to engine.
        
        Args:
            engine: RuleEngine instance (for accessing other handlers)
        """
        self._engine = engine
    
    def detect(
        self, 
        cv_text: str, 
        cv_structure: CVStructure, 
        rule: DetectionRule
    ) -> List[DetectedIssue]:
        """
        Detect using multiple conditions combined with logic.
        """
        issues = []
        config = rule.detection_config
        
        if self._engine is None:
            logger.error(f"CompositeHandler requires engine reference for {rule.issue_code}")
            return issues
        
        logic = config.get('logic', 'and')
        conditions = config.get('conditions', [])
        issue_when = config.get('issue_when', 'all_match')
        
        if not conditions:
            return issues
        
        condition_results = []
        
        for i, condition_config in enumerate(conditions):
            condition_type = condition_config.get('type')
            
            if not condition_type:
                continue
            
            handler = self._engine.handlers.get(condition_type)
            if not handler:
                logger.warning(f"No handler for condition type: {condition_type}")
                continue
            
            temp_rule = DetectionRule(
                issue_code=f"{rule.issue_code}_condition_{i}",
                display_name="",
                description="",
                detection_method=condition_type,
                detection_config=condition_config,
                severity=rule.severity,
                weight=0,
                can_auto_fix=False,
                auto_fix_type=None,
                static_tip="",
                user_effort="minimal",
                example_before=None,
                example_after=None,
                category_code="",
                category_name="",
                subcategory_code="",
                subcategory_name="",
            )
            
            condition_issues = handler.detect(cv_text, cv_structure, temp_rule)
            condition_results.append(len(condition_issues) > 0)
        
        if logic == 'and' or issue_when == 'all_match':
            should_trigger = all(condition_results)
        else:
            should_trigger = any(condition_results)
        
        if should_trigger:
            match_text = f"Composite condition met ({len([r for r in condition_results if r])}/{len(condition_results)} conditions)"
            
            issue = self.create_issue(
                rule=rule,
                match_text=match_text,
                details={
                    'logic': logic,
                    'condition_count': len(conditions),
                    'conditions_met': sum(condition_results),
                    'condition_results': condition_results
                }
            )
            issues.append(issue)
        
        return issues
