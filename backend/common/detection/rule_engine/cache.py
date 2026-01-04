"""
Rule Cache

In-memory cache for detection rules.
FOLLOWS: CatalogCache pattern from common/catalog/cache.py
Uses system_cache_control table for invalidation.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class DetectionRule:
    """
    Represents a detection rule loaded from database.
    """
    issue_code: str
    display_name: str
    description: str
    detection_method: str
    detection_config: Dict[str, Any]
    severity: str
    weight: int
    can_auto_fix: bool
    auto_fix_type: Optional[str]
    static_tip: str
    user_effort: str
    example_before: Optional[str]
    example_after: Optional[str]
    category_code: str
    category_name: str
    subcategory_code: str
    subcategory_name: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DetectionRule':
        """Create DetectionRule from database row dictionary."""
        return cls(
            issue_code=data.get('issue_code', ''),
            display_name=data.get('display_name', ''),
            description=data.get('description', ''),
            detection_method=data.get('detection_method', ''),
            detection_config=data.get('detection_config') or {},
            severity=data.get('severity', 'consider'),
            weight=data.get('weight', 5),
            can_auto_fix=data.get('can_auto_fix', False),
            auto_fix_type=data.get('auto_fix_type'),
            static_tip=data.get('static_tip', ''),
            user_effort=data.get('user_effort', 'medium'),
            example_before=data.get('example_before'),
            example_after=data.get('example_after'),
            category_code=data.get('category_code', ''),
            category_name=data.get('category_name', ''),
            subcategory_code=data.get('subcategory_code', ''),
            subcategory_name=data.get('subcategory_name', ''),
        )


class RuleCache:
    """
    In-memory cache for detection rules.
    
    Invalidation:
    - Compares local cache_version with database cache_version
    - If different, reloads all rules
    - To invalidate: UPDATE system_cache_control SET cache_version = cache_version + 1
    """
    
    def __init__(self):
        self._rules: List[DetectionRule] = []
        self._rules_by_code: Dict[str, DetectionRule] = {}
        self._rules_by_category: Dict[str, List[DetectionRule]] = {}
        self._cache_version: int = 0
        self._is_loaded: bool = False
    
    @property
    def is_loaded(self) -> bool:
        return self._is_loaded
    
    @property
    def cache_version(self) -> int:
        return self._cache_version
    
    def load(self, rules_data: List[Dict[str, Any]], cache_version: int) -> None:
        """
        Load rules into cache.
        
        Args:
            rules_data: List of rule dictionaries from database
            cache_version: Current cache version from system_cache_control
        """
        self._rules = []
        self._rules_by_code = {}
        self._rules_by_category = {}
        
        for data in rules_data:
            rule = DetectionRule.from_dict(data)
            self._rules.append(rule)
            self._rules_by_code[rule.issue_code] = rule
            
            if rule.category_code not in self._rules_by_category:
                self._rules_by_category[rule.category_code] = []
            self._rules_by_category[rule.category_code].append(rule)
        
        self._cache_version = cache_version
        self._is_loaded = True
        
        logger.info(f"Loaded {len(self._rules)} detection rules into cache (version {cache_version})")
    
    def get_all_rules(self) -> List[DetectionRule]:
        """Get all cached rules."""
        return self._rules.copy()
    
    def get_rule_by_code(self, issue_code: str) -> Optional[DetectionRule]:
        """Get a specific rule by issue code."""
        return self._rules_by_code.get(issue_code)
    
    def get_rules_by_category(self, category_code: str) -> List[DetectionRule]:
        """Get all rules for a category."""
        return self._rules_by_category.get(category_code, []).copy()
    
    def clear(self) -> None:
        """Clear the cache."""
        self._rules = []
        self._rules_by_code = {}
        self._rules_by_category = {}
        self._cache_version = 0
        self._is_loaded = False
