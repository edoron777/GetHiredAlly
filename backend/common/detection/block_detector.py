"""
CV Block Structure Detection Module

This module provides structured detection of CV blocks (sections) with
detailed metadata including line numbers, confidence scores, and 
hierarchical sub-blocks (jobs, education entries).

It WRAPS the existing section_extractor.py and bullet_extractor.py
functionality into a unified structure for use by all detectors.

Author: GetHiredAlly
Version: 1.0
Date: January 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

from backend.common.detection.section_extractor import extract_sections, CVStructure
from backend.common.detection.bullet_extractor import extract_bullets, BulletPoint


class BlockType(Enum):
    """Standard CV block types."""
    CONTACT = "contact"
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    CERTIFICATIONS = "certifications"
    PROJECTS = "projects"
    LANGUAGES = "languages"
    AWARDS = "awards"
    PUBLICATIONS = "publications"
    VOLUNTEER = "volunteer"
    INTERESTS = "interests"
    REFERENCES = "references"
    UNRECOGNIZED = "unrecognized"


@dataclass
class ContactInfo:
    """Extracted contact information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    start_line: int = 0
    end_line: int = 0


@dataclass
class EnhancedBullet:
    """Bullet point with analysis - wraps BulletPoint from bullet_extractor."""
    text: str
    line_number: int
    word_count: int = 0
    has_metrics: bool = False
    has_strong_verb: bool = False
    starts_with_verb: bool = False
    action_verb: Optional[str] = None
    metrics_found: List[str] = field(default_factory=list)
    parent_job_index: Optional[int] = None
    
    @classmethod
    def from_bullet_point(cls, bp: BulletPoint, parent_job_index: Optional[int] = None) -> 'EnhancedBullet':
        """Create from existing BulletPoint (from bullet_extractor.py)."""
        return cls(
            text=bp.text,
            line_number=bp.line_number,
            word_count=bp.word_count,
            has_metrics=bp.has_metrics,
            has_strong_verb=bp.has_strong_verb,
            starts_with_verb=bp.starts_with_verb,
            action_verb=getattr(bp, 'action_verb', None),
            metrics_found=getattr(bp, 'metrics_found', []),
            parent_job_index=parent_job_index
        )


@dataclass
class JobEntry:
    """A single job within the Experience block."""
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    dates: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    duration_months: Optional[int] = None
    location: Optional[str] = None
    bullets: List[EnhancedBullet] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    raw_text: str = ""
    job_index: int = 0


@dataclass
class EducationEntry:
    """A single education entry within the Education block."""
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[str] = None
    honors: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    raw_text: str = ""


@dataclass
class CertificationEntry:
    """A single certification entry."""
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None
    expiry: Optional[str] = None
    credential_id: Optional[str] = None
    start_line: int = 0
    end_line: int = 0


@dataclass
class SkillCategory:
    """A category of skills (e.g., "Programming Languages")."""
    category_name: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0


@dataclass
class CVBlock:
    """A single block (section) in the CV."""
    block_type: BlockType
    header_text: str = ""
    content: str = ""
    start_line: int = 0
    end_line: int = 0
    confidence: float = 1.0
    word_count: int = 0
    
    contact_info: Optional[ContactInfo] = None
    jobs: List[JobEntry] = field(default_factory=list)
    education_entries: List[EducationEntry] = field(default_factory=list)
    certifications: List[CertificationEntry] = field(default_factory=list)
    skill_categories: List[SkillCategory] = field(default_factory=list)
    
    needs_user_help: bool = False


@dataclass 
class StructureSummary:
    """High-level summary of CV structure."""
    has_contact: bool = False
    has_summary: bool = False
    has_experience: bool = False
    has_education: bool = False
    has_skills: bool = False
    has_certifications: bool = False
    total_blocks: int = 0
    total_jobs: int = 0
    total_bullets: int = 0
    total_lines: int = 0
    unrecognized_blocks: int = 0


@dataclass
class CVBlockStructure:
    """
    Complete CV structure with all blocks, sub-blocks, and metadata.
    This is the main output of detect_cv_blocks().
    """
    raw_text: str = ""
    
    blocks: List[CVBlock] = field(default_factory=list)
    
    contact_block: Optional[CVBlock] = None
    summary_block: Optional[CVBlock] = None
    experience_block: Optional[CVBlock] = None
    education_block: Optional[CVBlock] = None
    skills_block: Optional[CVBlock] = None
    
    all_jobs: List[JobEntry] = field(default_factory=list)
    all_bullets: List[EnhancedBullet] = field(default_factory=list)
    all_education: List[EducationEntry] = field(default_factory=list)
    all_certifications: List[CertificationEntry] = field(default_factory=list)
    
    summary: StructureSummary = field(default_factory=StructureSummary)
    
    processing_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def get_block_by_type(self, block_type: BlockType) -> Optional[CVBlock]:
        """Get a block by its type."""
        for block in self.blocks:
            if block.block_type == block_type:
                return block
        return None
    
    def get_blocks_by_type(self, block_type: BlockType) -> List[CVBlock]:
        """Get all blocks of a specific type (for multiples like UNRECOGNIZED)."""
        return [b for b in self.blocks if b.block_type == block_type]
    
    def get_bullets_for_job(self, job_index: int) -> List[EnhancedBullet]:
        """Get all bullets for a specific job."""
        return [b for b in self.all_bullets if b.parent_job_index == job_index]
    
    def get_line_content(self, line_number: int) -> Optional[str]:
        """Get content of a specific line."""
        lines = self.raw_text.split('\n')
        if 0 <= line_number - 1 < len(lines):
            return lines[line_number - 1]
        return None


CONFIDENCE_HIGH = 0.90
CONFIDENCE_MEDIUM = 0.70
CONFIDENCE_LOW = 0.50
