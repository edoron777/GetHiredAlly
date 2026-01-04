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
    Compatible with existing master_detector format.
    """
    issue_code: str
    issue_type: str
    match_text: str
    suggestion: str
    severity: str
    weight: int
    can_auto_fix: bool
    location: Optional[str] = None
    line_number: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'issue_code': self.issue_code,
            'issue_type': self.issue_type,
            'match_text': self.match_text,
            'suggestion': self.suggestion,
            'severity': self.severity,
            'weight': self.weight,
            'can_auto_fix': self.can_auto_fix,
        }
        if self.location:
            result['location'] = self.location
        if self.line_number is not None:
            result['line_number'] = self.line_number
        if self.details:
            result['details'] = self.details
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
        Extract contact section (typically first part of CV).
        
        CVStructure doesn't have explicit contact field, so we extract
        from the beginning of raw_text before first section.
        """
        if cv_structure.sections and len(cv_structure.sections) > 0:
            first_section_start = cv_structure.sections[0].start_pos if hasattr(cv_structure.sections[0], 'start_pos') else 0
            if first_section_start > 0:
                return cv_structure.raw_text[:first_section_start]
        
        return cv_structure.raw_text[:500] if cv_structure.raw_text else ''
    
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
        match_text: str,
        suggestion: Optional[str] = None,
        location: Optional[str] = None,
        line_number: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> DetectedIssue:
        """
        Create a DetectedIssue with consistent formatting.
        
        Args:
            rule: The detection rule that triggered
            match_text: Text that matched/triggered the issue
            suggestion: Override for static_tip (optional)
            location: Where in CV the issue was found
            line_number: Line number of issue
            details: Additional details
            
        Returns:
            DetectedIssue instance
        """
        return DetectedIssue(
            issue_code=rule.issue_code,
            issue_type=rule.issue_code,
            match_text=match_text,
            suggestion=suggestion or rule.static_tip,
            severity=rule.severity,
            weight=rule.weight,
            can_auto_fix=rule.can_auto_fix,
            location=location,
            line_number=line_number,
            details=details
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
