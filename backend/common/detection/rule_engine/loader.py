"""
Rule Loader

Loads detection rules from database with caching.
FOLLOWS: CatalogService singleton pattern from common/catalog/service.py

Usage:
    loader = get_rule_loader()
    rules = loader.get_all_rules()
"""

import logging
from typing import List, Optional

from .repository import RuleRepository
from .cache import RuleCache, DetectionRule

logger = logging.getLogger(__name__)


class RuleLoader:
    """
    Loads detection rules from database.
    
    Singleton pattern - use get_rule_loader() to get instance.
    
    Cache invalidation:
    - Automatically checks system_cache_control.cache_version
    - If version changed, reloads from database
    - Manual invalidation: call invalidate_cache()
    """
    
    _instance: Optional['RuleLoader'] = None
    
    def __init__(self, supabase_client=None):
        """
        Initialize RuleLoader.
        
        Args:
            supabase_client: Optional Supabase client for testing
        """
        self.repository = RuleRepository(supabase_client)
        self.cache = RuleCache()
        self._is_ready = False
    
    @classmethod
    def get_instance(cls, supabase_client=None) -> 'RuleLoader':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls(supabase_client)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None
    
    @property
    def is_ready(self) -> bool:
        """Check if loader is ready (cache loaded)."""
        return self._is_ready and self.cache.is_loaded
    
    def initialize(self) -> bool:
        """
        Initialize the loader by loading rules from database.
        
        Returns:
            True if initialization successful
        """
        try:
            self._refresh_cache_if_needed()
            self._is_ready = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize RuleLoader: {e}")
            return False
    
    def get_all_rules(self) -> List[DetectionRule]:
        """
        Get all active detection rules.
        
        Automatically refreshes cache if version changed.
        
        Returns:
            List of DetectionRule objects
        """
        print(f"[RuleLoader] Loading rules from database...")
        self._refresh_cache_if_needed()
        rules = self.cache.get_all_rules()
        print(f"[RuleLoader] Loaded {len(rules)} rules")
        for rule in rules:
            print(f"  - {rule.issue_code}: {rule.detection_config.get('type')}")
        return rules
    
    def get_rule_by_code(self, issue_code: str) -> Optional[DetectionRule]:
        """Get a specific rule by issue code."""
        self._refresh_cache_if_needed()
        return self.cache.get_rule_by_code(issue_code)
    
    def get_rules_by_category(self, category_code: str) -> List[DetectionRule]:
        """Get all rules for a category."""
        self._refresh_cache_if_needed()
        return self.cache.get_rules_by_category(category_code)
    
    def invalidate_cache(self) -> None:
        """Force cache refresh on next access."""
        self.cache.clear()
        logger.info("Detection rules cache invalidated")
    
    def _refresh_cache_if_needed(self) -> None:
        """Refresh cache if version changed or not loaded."""
        db_version = self.repository.fetch_cache_version()
        
        if not self.cache.is_loaded or self.cache.cache_version != db_version:
            logger.info(f"Refreshing detection rules cache (db version: {db_version}, cache version: {self.cache.cache_version})")
            rules_data = self.repository.fetch_all_detection_rules()
            self.cache.load(rules_data, db_version)


_loader_instance: Optional[RuleLoader] = None

def get_rule_loader() -> RuleLoader:
    """
    Get the RuleLoader singleton instance.
    
    Usage:
        from common.detection.rule_engine import get_rule_loader
        loader = get_rule_loader()
        rules = loader.get_all_rules()
    """
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = RuleLoader.get_instance()
        _loader_instance.initialize()
    return _loader_instance
