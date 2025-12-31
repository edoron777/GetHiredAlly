"""
CV Issue Catalog Module
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
from .repository import CatalogRepository
from .cache import CatalogCache
from .service import (
    CatalogService, 
    get_catalog_service, 
    init_catalog_service
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
    'AutoFixType',
    'CatalogRepository',
    'CatalogCache',
    'CatalogService',
    'get_catalog_service',
    'init_catalog_service'
]
