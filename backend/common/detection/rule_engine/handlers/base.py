"""
Base Handler

Abstract base class for all detection handlers.
Each handler type (regex, word_list, etc.) extends this class.

IMPORTANT: Uses CVStructure from section_extractor.py - DO NOT recreate.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import logging

from ...section_extractor import CVStructure, extract_sections

from ..cache import DetectionRule

logger = logging.getLogger(__name__)


@dataclass
class DetectedIssue:
    """
    Represents a detected issue.
    
    This is the output format for all handlers.
    MUST match format from old detectors exactly for frontend compatibility.
    """
    issue_code: str
    issue_type: str
    display_name: str
    description: str
    current: str
    suggestion: str
    severity: str
    weight: int
    can_auto_fix: bool
    is_highlightable: bool = False
    location: Optional[str] = None
    title: Optional[str] = None
    line_number: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    example_before: Optional[str] = None
    example_after: Optional[str] = None
    
    @property
    def match_text(self) -> str:
        """Alias for current (for logging compatibility)."""
        return self.current
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'issue_code': self.issue_code,
            'issue_type': self.issue_type,
            'display_name': self.display_name,
            'title': self.title or self.display_name,
            'description': self.description,
            'current': self.current,
            'current_text': self.current,
            'suggestion': self.suggestion,
            'static_tip': self.suggestion,
            'severity': self.severity,
            'weight': self.weight,
            'can_auto_fix': self.can_auto_fix,
            'is_auto_fixable': self.can_auto_fix,
            'is_highlightable': self.is_highlightable,
            'example_before': self.example_before or '',
            'example_after': self.example_after or '',
        }
        if self.location:
            result['location'] = self.location
        if self.line_number is not None:
            result['line_number'] = self.line_number
        if self.details:
            result.update(self.details)
        return result


class BaseHandler(ABC):
    """
    Abstract base class for detection handlers.
    
    Each handler implements detection for one type:
    - RegexHandler: Pattern matching
    - WordListHandler: Word list checking
    - PresenceHandler: Must contain pattern
    - AbsenceHandler: Must NOT contain pattern
    - CountHandler: Count items
    - LengthHandler: Min/max length
    - ConsistencyHandler: Format consistency
    - SectionRequiredHandler: Required sections
    - CompositeHandler: Multiple checks
    """
    
    @abstractmethod
    def detect(
        self, 
        cv_text: str, 
        cv_structure: CVStructure, 
        rule: DetectionRule
    ) -> List[DetectedIssue]:
        """
        Detect issues based on rule configuration.
        
        Args:
            cv_text: Full CV text
            cv_structure: Parsed CV structure (from section_extractor.py)
            rule: Detection rule with configuration
            
        Returns:
            List of detected issues (empty if no issues found)
        """
        pass
    
    def get_target_text(self, cv_structure: CVStructure, target_section: str) -> str:
        """
        Get text for the specified target section.
        
        Args:
            cv_structure: Parsed CV structure
            target_section: Section name from detection_config
            
        Returns:
            Text for that section (or full CV if 'all' or not found)
        """
        if target_section == 'all':
            return cv_structure.raw_text
        
        section_map = {
            'summary': cv_structure.summary,
            'experience': cv_structure.experience,
            'education': cv_structure.education,
            'skills': cv_structure.skills,
            'contact': self._extract_contact(cv_structure),
            'certifications': self._extract_certifications(cv_structure),
        }
        
        text = section_map.get(target_section)
        return text if text else cv_structure.raw_text
    
    def _extract_contact(self, cv_structure: CVStructure) -> str:
        """
        Extract contact information from CV.
        
        Contact info is typically at the TOP of the CV (name, email, phone, LinkedIn).
        We use first 800 characters which reliably captures all contact details.
        """
        raw_text = cv_structure.raw_text
        if not raw_text:
            return ''
        
        contact_text = raw_text[:800]
        return contact_text
    
    def _extract_certifications(self, cv_structure: CVStructure) -> str:
        """
        Extract certifications section.
        
        Look for section with 'certification' in name.
        """
        for section in cv_structure.sections:
            if hasattr(section, 'name') and 'certif' in section.name.lower():
                if hasattr(section, 'content'):
                    return section.content
        return ''
    
    def create_issue(
        self,
        rule: DetectionRule,
        current: str,
        description: Optional[str] = None,
        suggestion: Optional[str] = None,
        location: Optional[str] = None,
        title: Optional[str] = None,
        line_number: Optional[int] = None,
        is_highlightable: bool = False,
        details: Optional[Dict[str, Any]] = None
    ) -> DetectedIssue:
        """
        Create a DetectedIssue with consistent formatting.
        
        Args:
            rule: The detection rule that triggered
            current: SHORT text that matched (for highlighting)
            description: Description of issue (uses rule.description if not provided)
            suggestion: Override for static_tip (optional)
            location: Where in CV the issue was found
            title: Short title for the issue
            line_number: Line number of issue
            is_highlightable: Whether this text can be highlighted in document
            details: Additional details to include in output
            
        Returns:
            DetectedIssue instance
        """
        return DetectedIssue(
            issue_code=rule.issue_code,
            issue_type=rule.issue_code,
            display_name=rule.display_name,
            description=description or rule.description,
            current=current,
            suggestion=suggestion or rule.static_tip,
            severity=rule.severity,
            weight=rule.weight,
            can_auto_fix=rule.can_auto_fix,
            is_highlightable=is_highlightable,
            location=location,
            title=title or rule.display_name,
            line_number=line_number,
            details=details,
            example_before=rule.example_before,
            example_after=rule.example_after
        )
    
    def get_config_value(
        self, 
        rule: DetectionRule, 
        key: str, 
        default: Any = None
    ) -> Any:
        """
        Safely get a value from detection_config.
        
        Args:
            rule: Detection rule
            key: Config key to retrieve
            default: Default value if key not found
            
        Returns:
            Config value or default
        """
        return rule.detection_config.get(key, default)
    
    def validate_config(self, rule: DetectionRule, required_keys: List[str]) -> bool:
        """
        Validate that required config keys are present.
        
        Args:
            rule: Detection rule
            required_keys: List of required keys
            
        Returns:
            True if all required keys present, False otherwise
        """
        config = rule.detection_config
        missing = [k for k in required_keys if k not in config]
        
        if missing:
            logger.warning(
                f"Rule {rule.issue_code} missing required config keys: {missing}"
            )
            return False
        return True
