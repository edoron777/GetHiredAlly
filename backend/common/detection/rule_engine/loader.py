"""
Rule Loader - reads detection rules from database.

FOLLOWS: CatalogService pattern from common/catalog/
- Singleton pattern
- Repository for DB access
- Cache for performance
"""


class DetectionRule:
    """Represents a detection rule from database."""
    pass


class RuleLoader:
    """Loads detection rules from cv_issue_types table."""
    _instance = None
    pass
