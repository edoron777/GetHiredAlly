"""
CV Issue Catalog - Repository Layer

Handles all database access for the catalog.
Uses Supabase client to query the cv_issue_* tables.
"""

import logging
from typing import List, Dict, Optional
from .models import (
    Category, 
    Subcategory, 
    IssueType, 
    IssueExample, 
    LegacyMapping
)

logger = logging.getLogger(__name__)


class CatalogRepository:
    """
    Data access layer for CV Issue Catalog.
    
    All database queries are centralized here.
    The cache layer calls these methods to load data.
    """
    
    def __init__(self, supabase_client):
        """
        Initialize repository with Supabase client.
        
        Args:
            supabase_client: Initialized Supabase client
        """
        self.db = supabase_client
    
    def fetch_all_categories(self) -> List[Category]:
        """
        Fetch all active categories.
        
        Returns:
            List of Category objects ordered by display_order
        """
        try:
            response = self.db.table("cv_issue_categories") \
                .select("*") \
                .eq("is_active", True) \
                .order("display_order") \
                .execute()
            
            return [Category(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            raise
    
    def fetch_all_subcategories(self) -> List[Subcategory]:
        """
        Fetch all active subcategories with category info.
        
        Returns:
            List of Subcategory objects
        """
        try:
            response = self.db.table("cv_issue_subcategories") \
                .select("*, cv_issue_categories(code, display_name)") \
                .eq("is_active", True) \
                .order("display_order") \
                .execute()
            
            subcategories = []
            for row in response.data:
                cat_data = row.pop("cv_issue_categories", {}) or {}
                row["category_code"] = cat_data.get("code")
                row["category_name"] = cat_data.get("display_name")
                subcategories.append(Subcategory(**row))
            
            return subcategories
        except Exception as e:
            logger.error(f"Error fetching subcategories: {e}")
            raise
    
    def fetch_all_issues(self) -> List[IssueType]:
        """
        Fetch all active issues using the view.
        
        The view v_cv_issue_catalog joins all tables and
        includes category/subcategory names.
        
        Returns:
            List of IssueType objects with full metadata
        """
        try:
            response = self.db.table("v_cv_issue_catalog") \
                .select("*") \
                .execute()
            
            return [IssueType(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Error fetching issues from view: {e}")
            raise
    
    def fetch_issue_by_code(self, code: str) -> Optional[IssueType]:
        """
        Fetch a single issue by its code.
        
        Args:
            code: The issue_code to look up
            
        Returns:
            IssueType or None if not found
        """
        try:
            response = self.db.table("v_cv_issue_catalog") \
                .select("*") \
                .eq("issue_code", code) \
                .limit(1) \
                .execute()
            
            if response.data:
                return IssueType(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error fetching issue {code}: {e}")
            raise
    
    def fetch_legacy_mapping(self) -> Dict[str, str]:
        """
        Fetch all legacy code mappings.
        
        Returns:
            Dict mapping old_issue_code -> new_issue_code
        """
        try:
            response = self.db.table("cv_issue_legacy_mapping") \
                .select("old_issue_code, new_issue_code") \
                .execute()
            
            return {
                row["old_issue_code"]: row["new_issue_code"] 
                for row in response.data
            }
        except Exception as e:
            logger.error(f"Error fetching legacy mapping: {e}")
            raise
    
    def fetch_examples_for_issue(self, issue_type_id: int) -> List[IssueExample]:
        """
        Fetch examples for a specific issue type.
        
        Args:
            issue_type_id: The issue type ID
            
        Returns:
            List of IssueExample objects
        """
        try:
            response = self.db.table("cv_issue_examples") \
                .select("*") \
                .eq("issue_type_id", issue_type_id) \
                .eq("is_active", True) \
                .order("display_order") \
                .execute()
            
            return [IssueExample(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Error fetching examples for issue {issue_type_id}: {e}")
            raise
    
    def fetch_issues_by_category(self, category_code: str) -> List[IssueType]:
        """
        Fetch all issues in a category.
        
        Args:
            category_code: The category code (e.g., 'CONTACT')
            
        Returns:
            List of IssueType objects
        """
        try:
            response = self.db.table("v_cv_issue_catalog") \
                .select("*") \
                .eq("category_code", category_code) \
                .execute()
            
            return [IssueType(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Error fetching issues for category {category_code}: {e}")
            raise
    
    def fetch_issues_by_severity(self, severity: str) -> List[IssueType]:
        """
        Fetch all issues with a specific severity.
        
        Args:
            severity: The severity level (critical, important, consider, polish)
            
        Returns:
            List of IssueType objects
        """
        try:
            response = self.db.table("v_cv_issue_catalog") \
                .select("*") \
                .eq("severity", severity) \
                .execute()
            
            return [IssueType(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Error fetching issues for severity {severity}: {e}")
            raise
