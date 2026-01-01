"""
CV Issue Catalog - Service Layer

Main interface for the CV Issue Catalog.
This is what detection code and API routes should use.
"""

import logging
from typing import List, Optional, Dict, Any
from .models import (
    Category, 
    Subcategory, 
    IssueType, 
    CatalogSummary,
    SeverityConfig
)
from .cache import CatalogCache
from .repository import CatalogRepository

logger = logging.getLogger(__name__)


class CatalogService:
    """
    Business logic layer for CV Issue Catalog.
    
    This is the main interface that detection and scoring code should use.
    All queries go through the cache for performance.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._service_initialized = False
        return cls._instance
    
    def __init__(self, supabase_client=None):
        if self._service_initialized and supabase_client is None:
            return
        
        if supabase_client:
            self.repository = CatalogRepository(supabase_client)
            self.cache = CatalogCache()
            self._service_initialized = True
    
    def initialize(self) -> None:
        """Initialize the service by loading cache"""
        if not self._service_initialized:
            raise RuntimeError("Service not properly initialized with Supabase client")
        self.cache.load(self.repository)
        logger.info("CatalogService initialized")
    
    def refresh_cache(self) -> None:
        """Force refresh the cache from database"""
        self.cache.load(self.repository, force=True)
        logger.info("Catalog cache refreshed")
    
    @property
    def is_ready(self) -> bool:
        """Check if service is ready to use"""
        return self._service_initialized and self.cache.is_loaded
    
    def get_all_issues(self) -> List[IssueType]:
        """Get all active issue types"""
        return self.cache.get_all_issues()
    
    def get_issue_by_code(self, code: str) -> Optional[IssueType]:
        """
        Get issue by code.
        Automatically handles legacy code conversion.
        """
        normalized_code = self.cache.normalize_legacy_code(code)
        return self.cache.get_issue_by_code(normalized_code)
    
    def get_issues_by_category(self, category_code: str) -> List[IssueType]:
        """Get all issues in a category"""
        return self.cache.get_issues_by_category(category_code)
    
    def get_issues_by_severity(self, severity: str) -> List[IssueType]:
        """Get all issues with a severity level"""
        return self.cache.get_issues_by_severity(severity)
    
    def get_categories(self) -> List[Category]:
        """Get all categories"""
        return self.cache.get_categories()
    
    def get_subcategories(self) -> List[Subcategory]:
        """Get all subcategories"""
        return self.cache.get_subcategories()
    
    def get_summary(self) -> CatalogSummary:
        """Get catalog statistics"""
        return self.cache.get_summary()
    
    def normalize_issue_code(self, code: str) -> str:
        """Convert legacy code to new code if needed"""
        return self.cache.normalize_legacy_code(code)
    
    def enrich_detected_issue(self, detected_issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a detected issue with catalog metadata.
        
        Takes a raw detected issue (from detection code) and adds
        all metadata from the catalog (severity, weight, tip, etc.)
        
        Args:
            detected_issue: Dict with at least 'issue_type' key
            
        Returns:
            Enriched issue dict with all catalog metadata
        """
        issue_code = detected_issue.get('issue_type', '')
        
        normalized_code = self.cache.normalize_legacy_code(issue_code)
        detected_issue['issue_type'] = normalized_code
        
        catalog_entry = self.cache.get_issue_by_code(normalized_code)
        
        # DEBUG: Log enrichment
        logger.debug(f"Enriching {normalized_code}: catalog_entry={catalog_entry is not None}")
        
        if catalog_entry:
            detected_issue['severity'] = catalog_entry.severity
            detected_issue['weight'] = catalog_entry.weight
            detected_issue['display_name'] = catalog_entry.display_name
            detected_issue['category'] = catalog_entry.category_name
            detected_issue['subcategory'] = catalog_entry.subcategory_name
            detected_issue['can_auto_fix'] = catalog_entry.can_auto_fix
            detected_issue['auto_fix_type'] = catalog_entry.auto_fix_type
            detected_issue['user_effort'] = catalog_entry.user_effort
            detected_issue['detection_method'] = catalog_entry.detection_method
            
            if not detected_issue.get('suggestion') and catalog_entry.static_tip:
                detected_issue['suggestion'] = catalog_entry.static_tip
            
            if catalog_entry.example_before:
                detected_issue['example_before'] = catalog_entry.example_before
            
            if catalog_entry.example_after:
                detected_issue['example_after'] = catalog_entry.example_after
            
            if catalog_entry.ui_config:
                detected_issue['ui_config'] = catalog_entry.ui_config
            
            if catalog_entry.attributes:
                detected_issue['attributes'] = catalog_entry.attributes
        else:
            logger.warning(f"Unknown issue type: {normalized_code}")
            detected_issue['severity'] = 'consider'
            detected_issue['weight'] = 5
            detected_issue['display_name'] = normalized_code
            detected_issue['category'] = 'Other'
            detected_issue['can_auto_fix'] = False
        
        return detected_issue
    
    def enrich_all_issues(self, detected_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich a list of detected issues"""
        return [self.enrich_detected_issue(issue) for issue in detected_issues]
    
    def get_severity_config(self) -> Dict[str, SeverityConfig]:
        """Get severity display configuration for frontend"""
        return {
            'critical': SeverityConfig(
                label='Critical',
                color='text-red-600',
                bg='bg-red-50',
                border='border-red-200'
            ),
            'important': SeverityConfig(
                label='Important',
                color='text-orange-600',
                bg='bg-orange-50',
                border='border-orange-200'
            ),
            'consider': SeverityConfig(
                label='Consider',
                color='text-yellow-600',
                bg='bg-yellow-50',
                border='border-yellow-200'
            ),
            'polish': SeverityConfig(
                label='Polish',
                color='text-green-600',
                bg='bg-green-50',
                border='border-green-200'
            )
        }
    
    def get_severity_display(self, severity: str) -> str:
        """Get display label for a severity"""
        mapping = {
            'critical': 'Critical',
            'important': 'Important',
            'consider': 'Consider',
            'polish': 'Polish',
            'high': 'Important',
            'medium': 'Consider',
            'low': 'Polish'
        }
        return mapping.get(severity, severity.title())


_catalog_service: Optional[CatalogService] = None

def get_catalog_service() -> CatalogService:
    """Get the global CatalogService instance"""
    global _catalog_service
    if _catalog_service is None:
        _catalog_service = CatalogService()
    return _catalog_service

def init_catalog_service(supabase_client) -> CatalogService:
    """Initialize the global CatalogService with Supabase client"""
    global _catalog_service
    _catalog_service = CatalogService(supabase_client)
    _catalog_service.initialize()
    return _catalog_service
