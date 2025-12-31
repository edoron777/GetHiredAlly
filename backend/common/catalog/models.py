"""
CV Issue Catalog - Data Models

Pydantic models for the CV Issue Catalog system.
These models represent the data stored in the database.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    IMPORTANT = "important"
    CONSIDER = "consider"
    POLISH = "polish"


class DetectionMethod(str, Enum):
    """How the issue is detected"""
    REGEX = "regex"
    RULE = "rule"
    NLP = "nlp"
    AI = "ai"


class UserEffort(str, Enum):
    """Effort required from user to fix"""
    MINIMAL = "minimal"
    MEDIUM = "medium"
    EXTENSIVE = "extensive"


class AutoFixType(str, Enum):
    """Type of automatic fix available"""
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


class Category(BaseModel):
    """CV Issue Category model"""
    id: int
    code: str
    display_name: str
    description: Optional[str] = None
    display_order: int = 0
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True
    metadata: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class Subcategory(BaseModel):
    """CV Issue Subcategory model"""
    id: int
    category_id: int
    code: str
    display_name: str
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    category_code: Optional[str] = None
    category_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class IssueType(BaseModel):
    """CV Issue Type model - main catalog entry"""
    id: int
    issue_code: str
    display_name: str
    description: Optional[str] = None
    severity: str
    weight: int = 5
    can_auto_fix: bool = False
    auto_fix_type: Optional[str] = None
    detection_method: Optional[str] = None
    static_tip: Optional[str] = None
    user_effort: Optional[str] = None
    requires_user_input: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    attributes: Dict[str, Any] = {}
    ui_config: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    subcategory_id: Optional[int] = None
    subcategory_code: Optional[str] = None
    subcategory_name: Optional[str] = None
    category_id: Optional[int] = None
    category_code: Optional[str] = None
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    category_icon: Optional[str] = None
    
    class Config:
        from_attributes = True


class IssueExample(BaseModel):
    """Before/after example for an issue type"""
    id: int
    issue_type_id: int
    example_type: str = "before_after"
    before_text: Optional[str] = None
    after_text: Optional[str] = None
    explanation: Optional[str] = None
    context: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    
    class Config:
        from_attributes = True


class LegacyMapping(BaseModel):
    """Maps old issue codes to new codes"""
    id: int
    old_issue_code: str
    new_issue_code: str
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class CatalogSummary(BaseModel):
    """Summary statistics for the catalog"""
    total_categories: int
    total_subcategories: int
    total_issue_types: int
    issues_by_severity: Dict[str, int]
    issues_by_category: Dict[str, int]
    auto_fixable_count: int
    last_loaded: Optional[datetime] = None


class SeverityConfig(BaseModel):
    """UI configuration for a severity level"""
    label: str
    color: str
    bg: str
    border: str
