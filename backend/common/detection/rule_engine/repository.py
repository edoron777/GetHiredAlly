"""
Rule Repository

Database queries for detection rules.
FOLLOWS: CatalogRepository pattern from common/catalog/repository.py
"""

import os
import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)


def get_supabase_client() -> Optional[Client]:
    """Get Supabase client from environment."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        logger.warning("Supabase credentials not found in environment")
        return None
    
    return create_client(url, key)


class RuleRepository:
    """
    Database access for detection rules.
    
    Uses v_cv_detection_rules view created in DB-1.
    """
    
    def __init__(self, supabase_client=None):
        """
        Initialize repository.
        
        Args:
            supabase_client: Supabase client. If None, will get from environment.
        """
        self._client = supabase_client
        self._initialized = False
    
    def _get_client(self):
        """Get Supabase client (lazy initialization)."""
        if self._client is None:
            self._client = get_supabase_client()
        return self._client
    
    def fetch_all_detection_rules(self) -> List[Dict[str, Any]]:
        """
        Fetch all detection rules with non-empty detection_config.
        
        Returns:
            List of rule dictionaries from v_cv_detection_rules view
        """
        try:
            client = self._get_client()
            if client is None:
                logger.error("No Supabase client available")
                return []
            
            response = client.from_('v_cv_detection_rules') \
                .select('*') \
                .neq('detection_config', {}) \
                .execute()
            
            if response.data:
                logger.info(f"Fetched {len(response.data)} detection rules from database")
                return response.data
            
            logger.warning("No detection rules found with detection_config")
            return []
            
        except Exception as e:
            logger.error(f"Failed to fetch detection rules: {e}")
            return []
    
    def fetch_cache_version(self) -> int:
        """
        Fetch current cache version from system_cache_control.
        
        Returns:
            Current cache version number
        """
        try:
            client = self._get_client()
            if client is None:
                return 1
            
            response = client.from_('system_cache_control') \
                .select('cache_version') \
                .eq('cache_key', 'cv_detection_rules') \
                .single() \
                .execute()
            
            if response.data:
                return response.data.get('cache_version', 1)
            return 1
            
        except Exception as e:
            logger.warning(f"Failed to fetch cache version: {e}")
            return 1
