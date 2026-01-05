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
    
    # CVStructure has direct attributes for each section type (contact, summary, experience, etc.)
    # and a sections list with CVSection objects. We'll use both approaches.
    
    # Map of attribute name -> BlockType
    section_attr_map = {
        'contact': BlockType.CONTACT,
        'summary': BlockType.SUMMARY,
        'experience': BlockType.EXPERIENCE,
        'education': BlockType.EDUCATION,
        'skills': BlockType.SKILLS,
        'certifications': BlockType.CERTIFICATIONS,
    }
    
    # First, create blocks from direct attributes (these are the main sections)
    for attr_name, block_type in section_attr_map.items():
        content = getattr(cv_structure, attr_name, None)
        if not content or not isinstance(content, str):
            continue
        
        # Find line numbers for this content
        start_line, end_line = _find_content_lines(content, lines)
        
        block = CVBlock(
            block_type=block_type,
            header_text=attr_name.replace('_', ' ').title(),
            content=content,
            start_line=start_line,
            end_line=end_line,
            confidence=0.95,
            word_count=len(content.split()),
            needs_user_help=False
        )
        
        blocks.append(block)
    
    # Also check the sections list (List[CVSection]) for any additional sections
    cv_sections = getattr(cv_structure, 'sections', [])
    if cv_sections and isinstance(cv_sections, list):
        # Map CVSection.name to BlockType
        name_to_type = {
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
        
        # Track which block types we already have to avoid duplicates
        existing_types = {b.block_type for b in blocks}
        
        for cv_section in cv_sections:
            section_name = getattr(cv_section, 'name', '').lower()
            section_content = getattr(cv_section, 'content', '')
            
            if not section_content:
                continue
            
            # Determine block type
            block_type = name_to_type.get(section_name, BlockType.UNRECOGNIZED)
            
            # Skip if we already have this block type from direct attributes
            if block_type in existing_types and block_type != BlockType.UNRECOGNIZED:
                continue
            
            block = CVBlock(
                block_type=block_type,
                header_text=getattr(cv_section, 'header', section_name),
                content=section_content,
                start_line=getattr(cv_section, 'line_number', 0),
                end_line=getattr(cv_section, 'line_number', 0) + len(section_content.split('\n')),
                confidence=0.9 if block_type != BlockType.UNRECOGNIZED else 0.5,
                word_count=len(section_content.split()),
                needs_user_help=(block_type == BlockType.UNRECOGNIZED)
            )
            
            blocks.append(block)
            existing_types.add(block_type)
    
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


# ═══════════════════════════════════════════════════════════════════════════
# SUB-BLOCK EXTRACTION (Jobs, Education, Certifications)
# ═══════════════════════════════════════════════════════════════════════════

import re

def _extract_all_sub_blocks(result: CVBlockStructure, cv_structure: CVStructure, lines: List[str]) -> None:
    """
    Extract jobs, education entries, and certifications from blocks.
    
    Uses cv_structure.job_entries if available, otherwise falls back to
    parsing jobs directly from experience content.
    """
    
    # Extract jobs from Experience block
    if result.experience_block:
        job_entries = getattr(cv_structure, 'job_entries', [])
        
        if job_entries:
            # Use existing job_entries from section_extractor
            jobs = _extract_jobs_from_entries(job_entries, lines, result.experience_block.start_line)
        else:
            # Fallback: Parse jobs directly from experience content
            jobs = _extract_jobs_from_content(result.experience_block, lines)
        
        result.experience_block.jobs = jobs
        result.all_jobs = jobs
    
    # Extract education entries
    if result.education_block:
        entries = _extract_education_entries(result.education_block, lines)
        result.education_block.education_entries = entries
        result.all_education = entries
    
    # Extract certifications
    for block in result.blocks:
        if block.block_type == BlockType.CERTIFICATIONS:
            certs = _extract_certifications(block, lines)
            block.certifications = certs
            result.all_certifications = certs


def _extract_jobs_from_content(experience_block: CVBlock, lines: List[str]) -> List[JobEntry]:
    """
    Fallback: Parse jobs directly from experience content when job_entries is empty.
    
    Detects job boundaries by looking for date patterns like "Month YYYY - Present".
    """
    jobs = []
    content = experience_block.content
    
    if not content:
        return jobs
    
    content_lines = content.split('\n')
    
    # Pattern to detect job header lines (contains date range)
    date_pattern = re.compile(
        r'([A-Za-z]+\.?\s+\d{4})\s*[-–]\s*(Present|Current|[A-Za-z]+\.?\s+\d{4})',
        re.IGNORECASE
    )
    
    # Find lines that likely start a new job (contain date ranges)
    job_starts = []
    for i, line in enumerate(content_lines):
        if date_pattern.search(line):
            # Check if previous non-empty line might be the job title
            title_line = i
            if i > 0:
                for j in range(i - 1, max(0, i - 3), -1):
                    if content_lines[j].strip() and not date_pattern.search(content_lines[j]):
                        title_line = j
                        break
            job_starts.append(title_line)
    
    # If no jobs found by date, try to find by "at" pattern in first lines
    if not job_starts:
        for i, line in enumerate(content_lines):
            if re.search(r'\s+(?:at|@)\s+', line, re.IGNORECASE):
                job_starts.append(i)
    
    # Create jobs from detected boundaries
    for idx, start_idx in enumerate(job_starts):
        # End is next job start or end of content
        end_idx = job_starts[idx + 1] - 1 if idx + 1 < len(job_starts) else len(content_lines) - 1
        
        job_lines = content_lines[start_idx:end_idx + 1]
        
        job = JobEntry(job_index=idx)
        job.start_line = experience_block.start_line + start_idx
        job.end_line = experience_block.start_line + end_idx
        job.raw_text = '\n'.join(job_lines)
        
        _parse_job_details(job, job_lines)
        
        jobs.append(job)
    
    return jobs


def _extract_jobs_from_entries(job_entries: List[tuple], lines: List[str], experience_start: int) -> List[JobEntry]:
    """
    Extract jobs using the EXISTING job_entries from CVStructure.
    
    job_entries is List[Tuple[int, int]] where each tuple is (start_line, end_line).
    This is ALREADY parsed by section_extractor.py - we just need to extract details.
    """
    jobs = []
    
    if not job_entries:
        return jobs
    
    for idx, (start_line, end_line) in enumerate(job_entries):
        # Get the text for this job from lines
        job_lines = lines[start_line - 1:end_line]  # Convert to 0-indexed
        job_text = '\n'.join(job_lines)
        
        job = JobEntry(job_index=idx)
        job.start_line = start_line
        job.end_line = end_line
        job.raw_text = job_text
        
        # Parse job details from the text
        _parse_job_details(job, job_lines)
        
        jobs.append(job)
    
    return jobs


def _parse_job_details(job: JobEntry, job_lines: List[str]) -> None:
    """Parse job title, company, dates from job lines."""
    if not job_lines:
        return
    
    # First 1-3 lines usually contain title, company, dates
    header_text = '\n'.join(job_lines[:3])
    
    # Pattern: "Title at Company"
    title_company_match = re.search(r'^([A-Z][^,\n]+?)\s+(?:at|@)\s+([A-Z][^,\n(]+)', job_lines[0], re.IGNORECASE)
    if title_company_match:
        job.job_title = title_company_match.group(1).strip()
        job.company_name = title_company_match.group(2).strip()
    
    # Pattern: Look for date range anywhere in header
    date_match = re.search(
        r'([A-Za-z]+\.?\s+\d{4})\s*[-–]\s*(Present|Current|[A-Za-z]+\.?\s+\d{4})',
        header_text, re.IGNORECASE
    )
    if date_match:
        job.start_date = date_match.group(1)
        job.end_date = date_match.group(2)
        job.dates = f"{job.start_date} - {job.end_date}"
        job.is_current = job.end_date.lower() in ['present', 'current']
        job.duration_months = _calculate_duration_months(job.start_date, job.end_date)
    
    # If title not found, try first line (after removing dates)
    if not job.job_title and job_lines:
        potential_title = job_lines[0].strip()
        potential_title = re.sub(
            r'\(?[A-Za-z]+\s+\d{4}\s*[-–]\s*(?:Present|Current|[A-Za-z]+\s+\d{4})\)?',
            '', potential_title
        ).strip()
        potential_title = re.sub(r'\s*[-|]\s*$', '', potential_title).strip()
        if 3 < len(potential_title) < 100:
            job.job_title = potential_title
    
    # If company not found, try second line
    if not job.company_name and len(job_lines) > 1:
        potential_company = job_lines[1].strip()
        potential_company = re.sub(
            r'\(?[A-Za-z]+\s+\d{4}\s*[-–]\s*(?:Present|Current|[A-Za-z]+\s+\d{4})\)?',
            '', potential_company
        ).strip()
        if 2 < len(potential_company) < 100:
            if not potential_company.startswith(('•', '-', '*', '–', '►')):
                job.company_name = potential_company


def _calculate_duration_months(start_date: str, end_date: str) -> Optional[int]:
    """Calculate duration in months between two dates."""
    try:
        from datetime import datetime
        
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'june': 6, 'july': 7, 'august': 8, 'september': 9,
            'october': 10, 'november': 11, 'december': 12
        }
        
        def parse_date(date_str: str):
            date_str = date_str.lower().replace('.', '').strip()
            if date_str in ['present', 'current']:
                return datetime.now()
            parts = date_str.split()
            if len(parts) >= 2:
                month_str = parts[0][:3]
                year = int(parts[-1])
                month = month_map.get(month_str, 1)
                return datetime(year, month, 1)
            return None
        
        start = parse_date(start_date)
        end = parse_date(end_date)
        
        if start and end:
            return max(0, (end.year - start.year) * 12 + (end.month - start.month))
    except:
        pass
    return None


def _extract_education_entries(education_block: CVBlock, lines: List[str]) -> List[EducationEntry]:
    """Extract individual education entries from Education block."""
    entries = []
    content = education_block.content
    
    if not content:
        return entries
    
    # Split by double newlines
    edu_chunks = re.split(r'\n\s*\n', content)
    
    for chunk in edu_chunks:
        if not chunk.strip():
            continue
        entry = _parse_education_chunk(chunk, education_block.start_line, lines)
        if entry:
            entries.append(entry)
    
    return entries


def _parse_education_chunk(chunk: str, block_start_line: int, lines: List[str]) -> Optional[EducationEntry]:
    """Parse a chunk of text into an EducationEntry."""
    entry = EducationEntry()
    entry.raw_text = chunk
    chunk_lines = chunk.strip().split('\n')
    
    # Find line numbers
    first_line = chunk_lines[0].strip()
    for i, line in enumerate(lines):
        if first_line and first_line in line:
            entry.start_line = i + 1
            entry.end_line = entry.start_line + len(chunk_lines) - 1
            break
    
    # Look for degree patterns
    degree_patterns = [
        r"(Bachelor'?s?|Master'?s?|Ph\.?D\.?|MBA|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|Associate'?s?)\s+(?:of\s+|in\s+)?([A-Za-z\s]+)",
        r"(Bachelor|Master|Doctor)\s+of\s+([A-Za-z\s]+)",
    ]
    
    for pattern in degree_patterns:
        match = re.search(pattern, chunk, re.IGNORECASE)
        if match:
            entry.degree = match.group(1).strip()
            entry.field_of_study = match.group(2).strip()
            break
    
    # Look for institution
    inst_match = re.search(r'([A-Z][^,\n]*(?:University|College|Institute|School)[^,\n]*)', chunk, re.IGNORECASE)
    if inst_match:
        entry.institution = inst_match.group(1).strip()
    
    # Look for year
    year_match = re.search(r'\b(19|20)\d{2}\b', chunk)
    if year_match:
        entry.graduation_year = year_match.group(0)
    
    # Look for GPA
    gpa_match = re.search(r'GPA[:\s]+(\d+\.?\d*)', chunk, re.IGNORECASE)
    if gpa_match:
        entry.gpa = gpa_match.group(1)
    
    return entry if entry.institution or entry.degree else None


def _extract_certifications(cert_block: CVBlock, lines: List[str]) -> List[CertificationEntry]:
    """Extract certification entries from Certifications block."""
    certs = []
    content = cert_block.content
    
    if not content:
        return certs
    
    cert_lines = content.strip().split('\n')
    
    for cert_line in cert_lines:
        cert_line = cert_line.strip()
        if not cert_line or len(cert_line) < 5:
            continue
        
        cert_line = re.sub(r'^[•\-*►–]\s*', '', cert_line)
        cert = CertificationEntry()
        
        issuer_match = re.search(r'\(([^)]+)\)|[-–]\s*([A-Z][^\n,]+)', cert_line)
        if issuer_match:
            cert.issuer = (issuer_match.group(1) or issuer_match.group(2)).strip()
            cert.name = cert_line[:issuer_match.start()].strip()
        else:
            cert.name = cert_line
        
        date_match = re.search(r'\b(19|20)\d{2}\b', cert_line)
        if date_match:
            cert.date = date_match.group(0)
        
        if cert.name:
            certs.append(cert)
    
    return certs


def _extract_and_link_bullets(result: CVBlockStructure, cv_structure: CVStructure) -> None:
    """Extract bullets from Experience block and link to specific jobs."""
    if not result.experience_block:
        return
    
    # Use existing bullet_extractor
    all_bullets_bp = extract_bullets(result.experience_block.content)
    
    # Convert to EnhancedBullet and link to jobs
    for bp in all_bullets_bp:
        # Find which job this bullet belongs to based on line number
        parent_job_index = _find_parent_job(bp.line_number, result.all_jobs, result.experience_block.start_line)
        
        enhanced = EnhancedBullet.from_bullet_point(bp, parent_job_index)
        
        # Add to the job's bullet list
        if parent_job_index is not None and parent_job_index < len(result.all_jobs):
            result.all_jobs[parent_job_index].bullets.append(enhanced)
        
        result.all_bullets.append(enhanced)


def _find_parent_job(bullet_line: int, jobs: List[JobEntry], block_start_line: int) -> Optional[int]:
    """Find which job a bullet belongs to based on line numbers."""
    if not jobs:
        return None
    
    # Bullet line from extract_bullets is relative to the content passed
    # We need to convert to absolute line number
    absolute_line = block_start_line + bullet_line - 1
    
    # Find the job that contains this line
    for job in jobs:
        if job.start_line <= absolute_line <= job.end_line:
            return job.job_index
    
    # If not found within ranges, find the closest preceding job
    for job in reversed(jobs):
        if job.start_line <= absolute_line:
            return job.job_index
    
    return 0  # Default to first job


# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS FOR DETECTORS
# ═══════════════════════════════════════════════════════════════════════════

def get_experience_text(cv_block_structure: CVBlockStructure) -> str:
    """Get just the experience section text. For detectors that analyze experience."""
    if cv_block_structure.experience_block:
        return cv_block_structure.experience_block.content
    return ""


def get_education_text(cv_block_structure: CVBlockStructure) -> str:
    """Get just the education section text. For detectors that analyze education."""
    if cv_block_structure.education_block:
        return cv_block_structure.education_block.content
    return ""


def get_summary_text(cv_block_structure: CVBlockStructure) -> str:
    """Get just the summary section text. For detectors that analyze summary."""
    if cv_block_structure.summary_block:
        return cv_block_structure.summary_block.content
    return ""


def get_skills_text(cv_block_structure: CVBlockStructure) -> str:
    """Get just the skills section text. For detectors that analyze skills."""
    if cv_block_structure.skills_block:
        return cv_block_structure.skills_block.content
    return ""


def get_block_text(cv_block_structure: CVBlockStructure, block_type: BlockType) -> str:
    """Get text for any block type."""
    block = cv_block_structure.get_block_by_type(block_type)
    return block.content if block else ""


def get_all_bullet_texts(cv_block_structure: CVBlockStructure) -> List[str]:
    """Get all bullet point texts as a list of strings."""
    return [b.text for b in cv_block_structure.all_bullets]


def get_bullets_for_analysis(cv_block_structure: CVBlockStructure) -> List[Dict[str, Any]]:
    """Get bullets in a format suitable for analysis."""
    return [
        {
            'text': b.text,
            'line_number': b.line_number,
            'has_metrics': b.has_metrics,
            'has_strong_verb': b.has_strong_verb,
            'starts_with_verb': b.starts_with_verb,
            'action_verb': b.action_verb,
            'job_index': b.parent_job_index,
            'word_count': b.word_count
        }
        for b in cv_block_structure.all_bullets
    ]


def has_section(cv_block_structure: CVBlockStructure, block_type: BlockType) -> bool:
    """Check if CV has a specific section type."""
    return cv_block_structure.get_block_by_type(block_type) is not None


def get_structure_issues(cv_block_structure: CVBlockStructure) -> List[Dict[str, Any]]:
    """Identify structural issues based on detected structure."""
    issues = []
    summary = cv_block_structure.summary
    
    if not summary.has_contact:
        issues.append({
            'issue_type': 'missing_section',
            'severity': 'critical',
            'section': 'contact',
            'message': 'CV is missing contact information'
        })
    
    if not summary.has_experience:
        issues.append({
            'issue_type': 'missing_section',
            'severity': 'major',
            'section': 'experience',
            'message': 'CV is missing work experience section'
        })
    
    if not summary.has_education:
        issues.append({
            'issue_type': 'missing_section',
            'severity': 'minor',
            'section': 'education',
            'message': 'CV is missing education section'
        })
    
    if summary.unrecognized_blocks > 0:
        issues.append({
            'issue_type': 'unrecognized_sections',
            'severity': 'info',
            'count': summary.unrecognized_blocks,
            'message': f'CV has {summary.unrecognized_blocks} unrecognized section(s)'
        })
    
    return issues


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Main function
    'detect_cv_blocks',
    
    # Data classes
    'CVBlockStructure',
    'CVBlock',
    'BlockType',
    'JobEntry',
    'EducationEntry',
    'CertificationEntry',
    'EnhancedBullet',
    'ContactInfo',
    'SkillCategory',
    'StructureSummary',
    
    # Constants
    'CONFIDENCE_HIGH',
    'CONFIDENCE_MEDIUM',
    'CONFIDENCE_LOW',
    
    # Utility functions
    'get_experience_text',
    'get_education_text',
    'get_summary_text',
    'get_skills_text',
    'get_block_text',
    'get_all_bullet_texts',
    'get_bullets_for_analysis',
    'has_section',
    'get_structure_issues',
]
