"""
Rule Engine

Main orchestrator for database-driven CV detection.
Loads rules from database and applies appropriate handlers.

IMPORTANT: Uses CVStructure from section_extractor.py
"""

import logging
from typing import List, Dict, Any

from .loader import get_rule_loader, RuleLoader
from .cache import DetectionRule
from .handlers import (
    BaseHandler, DetectedIssue,
    RegexHandler, WordListHandler, PresenceHandler,
    AbsenceHandler, CountHandler, LengthHandler,
    ConsistencyHandler, SectionRequiredHandler, CompositeHandler
)

from ..section_extractor import extract_sections, CVStructure

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    Database-driven detection engine.
    
    Reads detection rules from cv_issue_types.detection_config
    and applies them to CV text.
    
    DETERMINISTIC: Same CV text + Same rules = Same issues (always)
    
    Usage:
        engine = RuleEngine()
        issues = engine.detect_all_issues(cv_text)
    """
    
    def __init__(self, loader: RuleLoader = None):
        """
        Initialize RuleEngine.
        
        Args:
            loader: Optional RuleLoader (uses singleton if not provided)
        """
        self.loader = loader or get_rule_loader()
        
        self.handlers: Dict[str, BaseHandler] = {
            'regex': RegexHandler(),
            'word_list': WordListHandler(),
            'presence': PresenceHandler(),
            'absence': AbsenceHandler(),
            'count': CountHandler(),
            'length': LengthHandler(),
            'consistency': ConsistencyHandler(),
            'section_required': SectionRequiredHandler(),
        }
        
        self.handlers['composite'] = CompositeHandler(self)
    
    def detect_all_issues(self, cv_text: str) -> List[Dict[str, Any]]:
        """
        Apply ALL active rules from database to CV text.
        
        Args:
            cv_text: Full CV text to analyze
            
        Returns:
            List of detected issues as dictionaries
        """
        if not cv_text or not cv_text.strip():
            logger.warning("Empty CV text provided to RuleEngine")
            return []
        
        cv_structure = extract_sections(cv_text)
        
        rules = self.loader.get_all_rules()
        
        if not rules:
            logger.warning("No detection rules loaded from database")
            return []
        
        print(f"[RuleEngine] Starting detection with {len(rules)} rules")
        logger.info(f"Applying {len(rules)} detection rules from database")
        logger.info("=" * 60)
        logger.info("[RULE ENGINE] APPLYING RULES:")
        logger.info("=" * 60)
        
        all_issues: List[DetectedIssue] = []
        
        for rule in rules:
            try:
                config_type = rule.detection_config.get('type', 'NO_TYPE')
                logger.info(f"  Evaluating [{rule.issue_code}] handler={config_type}")
                issues = self._apply_rule(cv_text, cv_structure, rule)
                if issues:
                    logger.info(f"    -> DETECTED {len(issues)} issue(s)")
                    for issue in issues:
                        logger.info(f"       match: {issue.match_text[:50] if issue.match_text else 'N/A'}...")
                else:
                    logger.info(f"    -> no issues found")
                all_issues.extend(issues)
            except Exception as e:
                logger.error(f"Error applying rule {rule.issue_code}: {e}", exc_info=True)
        
        logger.info("=" * 60)
        logger.info(f"[RULE ENGINE] TOTAL: {len(all_issues)} issues detected")
        logger.info("=" * 60)
        
        return [issue.to_dict() for issue in all_issues]
    
    def _apply_rule(
        self, 
        cv_text: str, 
        cv_structure: CVStructure, 
        rule: DetectionRule
    ) -> List[DetectedIssue]:
        """
        Apply a single detection rule.
        """
        config = rule.detection_config
        detection_type = config.get('type')
        
        if not detection_type:
            logger.debug(f"Rule {rule.issue_code} has no detection type in config")
            return []
        
        handler = self.handlers.get(detection_type)
        
        if not handler:
            logger.warning(f"No handler for detection type: {detection_type}")
            return []
        
        return handler.detect(cv_text, cv_structure, rule)
    
    def detect_single_issue(
        self, 
        cv_text: str, 
        issue_code: str
    ) -> List[Dict[str, Any]]:
        """
        Apply a single rule by issue code (for testing).
        """
        rule = self.loader.get_rule_by_code(issue_code)
        
        if not rule:
            logger.warning(f"Rule not found: {issue_code}")
            return []
        
        cv_structure = extract_sections(cv_text)
        issues = self._apply_rule(cv_text, cv_structure, rule)
        
        return [issue.to_dict() for issue in issues]
    
    def get_loaded_rules_count(self) -> int:
        """Get count of loaded rules (for debugging)."""
        return len(self.loader.get_all_rules())
    
    def invalidate_cache(self) -> None:
        """Force cache refresh."""
        self.loader.invalidate_cache()


def get_rule_engine() -> RuleEngine:
    """Get a RuleEngine instance."""
    return RuleEngine()
