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


# ═══════════════════════════════════════════════════════════════════════════
# MAIN DETECTION FUNCTION
# ═══════════════════════════════════════════════════════════════════════════

def detect_cv_blocks(cv_text: str) -> CVBlockStructure:
    """
    Main entry point for CV block structure detection.
    
    This function wraps the existing section_extractor.py functionality
    and adds enhanced metadata including line numbers, sub-blocks (jobs,
    education entries), and confidence scores.
    
    Args:
        cv_text: Raw CV text content
        
    Returns:
        CVBlockStructure with all detected blocks and metadata
    """
    import time
    start_time = time.time()
    
    result = CVBlockStructure(raw_text=cv_text)
    
    try:
        # Step 1: Get lines for line number tracking
        lines = cv_text.split('\n')
        result.summary.total_lines = len(lines)
        
        # Step 2: Use existing section extractor
        cv_structure = extract_sections(cv_text)
        
        # Step 3: Convert to our enhanced block structure
        result.blocks = _convert_sections_to_blocks(cv_structure, lines)
        
        # Step 4: Set quick-access references
        _set_block_references(result)
        
        # Step 5: Extract sub-blocks (jobs, education entries)
        # CRITICAL: Pass cv_structure because it has job_entries with line boundaries!
        _extract_all_sub_blocks(result, cv_structure, lines)
        
        # Step 6: Extract and link bullets
        _extract_and_link_bullets(result, cv_structure)
        
        # Step 7: Build summary
        _build_summary(result)
        
    except Exception as e:
        result.errors.append(f"Detection error: {str(e)}")
    
    result.processing_time_ms = (time.time() - start_time) * 1000
    return result


def _convert_sections_to_blocks(cv_structure: CVStructure, lines: List[str]) -> List[CVBlock]:
    """Convert CVStructure sections to CVBlock list with line numbers."""
    blocks = []
    
    # Map section names to BlockType
    section_type_map = {
        'contact': BlockType.CONTACT,
        'summary': BlockType.SUMMARY,
        'professional_summary': BlockType.SUMMARY,
        'objective': BlockType.SUMMARY,
        'experience': BlockType.EXPERIENCE,
        'work_experience': BlockType.EXPERIENCE,
        'professional_experience': BlockType.EXPERIENCE,
        'employment': BlockType.EXPERIENCE,
        'education': BlockType.EDUCATION,
        'skills': BlockType.SKILLS,
        'technical_skills': BlockType.SKILLS,
        'core_competencies': BlockType.SKILLS,
        'certifications': BlockType.CERTIFICATIONS,
        'certificates': BlockType.CERTIFICATIONS,
        'projects': BlockType.PROJECTS,
        'languages': BlockType.LANGUAGES,
        'awards': BlockType.AWARDS,
        'publications': BlockType.PUBLICATIONS,
        'volunteer': BlockType.VOLUNTEER,
        'interests': BlockType.INTERESTS,
        'references': BlockType.REFERENCES,
    }
    
    # Get sections from cv_structure
    # Note: Adapt based on actual CVStructure attributes from section_extractor.py
    sections = getattr(cv_structure, 'sections', {})
    if not sections and hasattr(cv_structure, '__dict__'):
        sections = cv_structure.__dict__
    
    for section_name, section_content in sections.items():
        if not section_content:
            continue
            
        # Determine block type
        section_lower = section_name.lower().replace('_', ' ').replace('-', ' ')
        block_type = BlockType.UNRECOGNIZED
        confidence = 0.5
        
        for key, btype in section_type_map.items():
            if key in section_lower:
                block_type = btype
                confidence = 0.9
                break
        
        # Find line numbers for this content
        start_line, end_line = _find_content_lines(section_content, lines)
        
        block = CVBlock(
            block_type=block_type,
            header_text=section_name,
            content=section_content if isinstance(section_content, str) else str(section_content),
            start_line=start_line,
            end_line=end_line,
            confidence=confidence,
            word_count=len(str(section_content).split()),
            needs_user_help=(block_type == BlockType.UNRECOGNIZED)
        )
        
        blocks.append(block)
    
    # Sort blocks by start_line
    blocks.sort(key=lambda b: b.start_line)
    
    return blocks


def _find_content_lines(content: str, lines: List[str]) -> tuple:
    """Find start and end line numbers for content within lines."""
    if not content or not lines:
        return (0, 0)
    
    content_str = str(content)
    content_first_line = content_str.split('\n')[0].strip()
    
    start_line = 0
    for i, line in enumerate(lines, 1):
        if content_first_line and content_first_line in line:
            start_line = i
            break
    
    if start_line == 0:
        return (0, 0)
    
    # Count lines in content
    content_lines = len(content_str.split('\n'))
    end_line = min(start_line + content_lines - 1, len(lines))
    
    return (start_line, end_line)


def _set_block_references(result: CVBlockStructure) -> None:
    """Set quick-access block references."""
    for block in result.blocks:
        if block.block_type == BlockType.CONTACT:
            result.contact_block = block
        elif block.block_type == BlockType.SUMMARY:
            result.summary_block = block
        elif block.block_type == BlockType.EXPERIENCE:
            result.experience_block = block
        elif block.block_type == BlockType.EDUCATION:
            result.education_block = block
        elif block.block_type == BlockType.SKILLS:
            result.skills_block = block


def _build_summary(result: CVBlockStructure) -> None:
    """Build the StructureSummary."""
    result.summary.has_contact = result.contact_block is not None
    result.summary.has_summary = result.summary_block is not None
    result.summary.has_experience = result.experience_block is not None
    result.summary.has_education = result.education_block is not None
    result.summary.has_skills = result.skills_block is not None
    result.summary.has_certifications = any(b.block_type == BlockType.CERTIFICATIONS for b in result.blocks)
    result.summary.total_blocks = len(result.blocks)
    result.summary.total_jobs = len(result.all_jobs)
    result.summary.total_bullets = len(result.all_bullets)
    result.summary.unrecognized_blocks = len([b for b in result.blocks if b.block_type == BlockType.UNRECOGNIZED])


def _extract_all_sub_blocks(result: CVBlockStructure, cv_structure: CVStructure, lines: List[str]) -> None:
    """Extract jobs using cv_structure.job_entries for boundaries. Implemented in PHASE1-3#4."""
    pass


def _extract_and_link_bullets(result: CVBlockStructure, cv_structure: CVStructure) -> None:
    """Extract bullets and link to jobs. Implemented in PHASE1-3#4."""
    pass
