"""
CV Issue Catalog Module

Provides database-backed catalog of CV issue types with:
- In-memory caching for performance
- Legacy code mapping for backward compatibility
- Rich metadata for each issue type
"""

from .models import (
    Category,
    Subcategory,
    IssueType,
    IssueExample,
    LegacyMapping,
    CatalogSummary,
    SeverityConfig,
    Severity,
    DetectionMethod,
    UserEffort,
    AutoFixType
)

__all__ = [
    'Category',
    'Subcategory', 
    'IssueType',
    'IssueExample',
    'LegacyMapping',
    'CatalogSummary',
    'SeverityConfig',
    'Severity',
    'DetectionMethod',
    'UserEffort',
    'AutoFixType'
]
