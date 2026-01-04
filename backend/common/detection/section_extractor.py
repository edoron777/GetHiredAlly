"""
CV Section Extractor

Identifies and extracts CV sections using header pattern matching.
100% CODE - No AI - Deterministic results.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .word_lists import (
    SUMMARY_HEADERS,
    EXPERIENCE_HEADERS,
    EDUCATION_HEADERS,
    SKILLS_HEADERS,
)


@dataclass
class CVSection:
    """A single CV section."""
    name: str
    header: str
    content: str
    start_pos: int
    end_pos: int
    line_number: int


@dataclass
class CVStructure:
    """Parsed CV structure with all sections."""
    raw_text: str
    sections: List[CVSection] = field(default_factory=list)
    
    summary: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None
    
    has_summary: bool = False
    has_experience: bool = False
    has_education: bool = False
    has_skills: bool = False
    
    section_order: List[str] = field(default_factory=list)


def _normalize_header(text: str) -> str:
    """Normalize header text for comparison."""
    return text.lower().strip().rstrip(':').strip()


def _is_header_line(line: str) -> bool:
    """Check if a line looks like a section header."""
    line = line.strip()
    
    if not line:
        return False
    
    if len(line) > 50:
        return False
    
    if line.isupper() and len(line) > 3:
        return True
    
    if line.endswith(':'):
        return True
    
    normalized = _normalize_header(line)
    all_headers = SUMMARY_HEADERS + EXPERIENCE_HEADERS + EDUCATION_HEADERS + SKILLS_HEADERS
    
    for header in all_headers:
        if normalized == header or normalized.startswith(header):
            return True
    
    return False


def _identify_section_type(header: str) -> Optional[str]:
    """Identify what type of section this header represents."""
    normalized = _normalize_header(header)
    
    for h in SUMMARY_HEADERS:
        if normalized == h or normalized.startswith(h):
            return 'summary'
    
    for h in EXPERIENCE_HEADERS:
        if normalized == h or normalized.startswith(h):
            return 'experience'
    
    for h in EDUCATION_HEADERS:
        if normalized == h or normalized.startswith(h):
            return 'education'
    
    for h in SKILLS_HEADERS:
        if normalized == h or normalized.startswith(h):
            return 'skills'
    
    return None


def _extract_experience_by_pattern(text: str) -> Optional[str]:
    """
    Fallback: Extract experience content by detecting employment patterns.
    
    Used when no explicit "Experience" header is found.
    Looks for patterns like:
    - Company name + date range (e.g., "Citi ... Jul 2020 - Present")
    - Job title patterns (e.g., "VP, Cybersecurity")
    - Employment duration (e.g., "5 years 4 months")
    """
    employment_date_pattern = re.compile(
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[-–]\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
        re.IGNORECASE
    )
    
    year_range_pattern = re.compile(r'\b(19|20)\d{2}\s*[-–]\s*(Present|(19|20)\d{2})\b', re.IGNORECASE)
    
    lines = text.split('\n')
    experience_lines = []
    in_experience = False
    experience_start = None
    
    stop_headers = ['education', 'certifications', 'skills', 'references', 'hobbies', 'interests', 'awards']
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        if any(header in line_lower for header in stop_headers) and len(line.strip()) < 40:
            if in_experience:
                break
        
        if employment_date_pattern.search(line) or year_range_pattern.search(line):
            if not in_experience:
                in_experience = True
                experience_start = max(0, i - 2)
                for prev_line in lines[experience_start:i]:
                    experience_lines.append(prev_line)
            experience_lines.append(line)
        elif in_experience:
            experience_lines.append(line)
    
    if experience_lines:
        return '\n'.join(experience_lines).strip()
    return None


def extract_sections(text: str) -> CVStructure:
    """
    Extract all sections from CV text.
    
    This is the MAIN function for section extraction.
    100% deterministic - same text → same result.
    
    Args:
        text: Full CV text
        
    Returns:
        CVStructure with all identified sections
    """
    structure = CVStructure(raw_text=text)
    lines = text.split('\n')
    
    current_section = None
    current_content = []
    current_start = 0
    current_line = 0
    
    for i, line in enumerate(lines):
        if _is_header_line(line):
            if current_section:
                content = '\n'.join(current_content).strip()
                section_type = _identify_section_type(current_section)
                
                section = CVSection(
                    name=section_type or 'other',
                    header=current_section,
                    content=content,
                    start_pos=current_start,
                    end_pos=current_start + len(content),
                    line_number=current_line,
                )
                structure.sections.append(section)
                
                if section_type == 'summary':
                    structure.summary = content
                    structure.has_summary = True
                    structure.section_order.append('summary')
                elif section_type == 'experience':
                    structure.experience = content
                    structure.has_experience = True
                    structure.section_order.append('experience')
                elif section_type == 'education':
                    structure.education = content
                    structure.has_education = True
                    structure.section_order.append('education')
                elif section_type == 'skills':
                    structure.skills = content
                    structure.has_skills = True
                    structure.section_order.append('skills')
            
            current_section = line.strip()
            current_content = []
            current_start = sum(len(l) + 1 for l in lines[:i])
            current_line = i + 1
        else:
            current_content.append(line)
    
    if current_section and current_content:
        content = '\n'.join(current_content).strip()
        section_type = _identify_section_type(current_section)
        
        section = CVSection(
            name=section_type or 'other',
            header=current_section,
            content=content,
            start_pos=current_start,
            end_pos=len(text),
            line_number=current_line,
        )
        structure.sections.append(section)
        
        if section_type == 'summary':
            structure.summary = content
            structure.has_summary = True
            structure.section_order.append('summary')
        elif section_type == 'experience':
            structure.experience = content
            structure.has_experience = True
            structure.section_order.append('experience')
        elif section_type == 'education':
            structure.education = content
            structure.has_education = True
            structure.section_order.append('education')
        elif section_type == 'skills':
            structure.skills = content
            structure.has_skills = True
            structure.section_order.append('skills')
    
    if not structure.has_experience:
        fallback_experience = _extract_experience_by_pattern(text)
        if fallback_experience:
            structure.experience = fallback_experience
            structure.has_experience = True
            structure.section_order.append('experience')
    
    return structure


def get_section_issues(structure: CVStructure) -> List[Dict]:
    """
    Generate issues based on section analysis.
    
    Returns list of issue dictionaries with issue_type.
    """
    issues = []
    
    if not structure.has_summary:
        issues.append({
            'issue_type': 'CONTENT_MISSING_SUMMARY',
            'location': 'Summary Section',
            'description': 'No summary/profile section found',
            'current': '',
            'is_highlightable': False,
        })
    elif structure.summary:
        word_count = len(structure.summary.split())
        if word_count < 30:
            issues.append({
                'issue_type': 'CONTENT_SHORT_SUMMARY',
                'location': 'Summary Section',
                'description': f'Summary is too short ({word_count} words, recommend 30-60)',
                'current': structure.summary[:100] if len(structure.summary) > 100 else structure.summary,
                'is_highlightable': True,
            })
        elif word_count > 80:
            issues.append({
                'issue_type': 'LENGTH_SUMMARY_TOO_LONG',
                'location': 'Professional Summary',
                'description': f'Summary is {word_count} words. Summaries over 80 words become walls of text that recruiters skip.',
                'current': structure.summary[:150] + '...' if len(structure.summary) > 150 else structure.summary,
                'is_highlightable': True,
            })
    
    if 'education' in structure.section_order and 'experience' in structure.section_order:
        edu_idx = structure.section_order.index('education')
        exp_idx = structure.section_order.index('experience')
        
        if edu_idx < exp_idx:
            if structure.experience and len(structure.experience.split()) > 50:
                issues.append({
                    'issue_type': 'FORMAT_POOR_VISUAL_HIERARCHY',
                    'location': 'CV Structure',
                    'description': 'Education appears before Experience - consider reordering for experienced professionals',
                    'current': '',
                    'is_highlightable': False,
                })
    
    return issues


def get_word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def get_cv_length_issues(text: str) -> List[Dict]:
    """Check if CV is too long or too short."""
    issues = []
    word_count = get_word_count(text)
    
    if word_count > 1000:
        issues.append({
            'issue_type': 'LENGTH_CV_TOO_LONG',
            'location': 'Overall CV',
            'description': f'CV is {word_count} words - consider condensing to under 800 words',
            'current': '',
            'is_highlightable': False,
            'meta_info': {'word_count': word_count},
        })
    elif word_count < 200:
        issues.append({
            'issue_type': 'LENGTH_CV_TOO_SHORT',
            'location': 'Overall CV',
            'description': f'CV is only {word_count} words - consider adding more detail',
            'current': '',
            'is_highlightable': False,
            'meta_info': {'word_count': word_count},
        })
    
    return issues


def get_experience_detail_issues(text: str) -> List[Dict]:
    """
    Check if old jobs have too much detail.
    
    Args:
        text: Full CV text
        
    Returns:
        List of LENGTH_EXPERIENCE_TOO_DETAILED issues
    """
    import datetime
    issues = []
    current_year = datetime.datetime.now().year
    
    year_pattern = re.compile(r'\b(19|20)\d{2}\b')
    job_section_pattern = re.compile(
        r'^([A-Z][a-zA-Z\s,]+)\s*[-–|]\s*.*?((?:19|20)\d{2})',
        re.MULTILINE
    )
    
    lines = text.split('\n')
    
    for match in job_section_pattern.finditer(text):
        job_title = match.group(1).strip()
        year_str = match.group(2)
        
        try:
            job_year = int(year_str)
            years_ago = current_year - job_year
            
            if years_ago > 10:
                start_pos = match.end()
                next_job = job_section_pattern.search(text[start_pos:])
                
                if next_job:
                    section_text = text[start_pos:start_pos + next_job.start()]
                else:
                    section_text = text[start_pos:start_pos + 500]
                
                bullet_count = len(re.findall(r'^\s*[•\-\*]\s+', section_text, re.MULTILINE))
                
                if bullet_count > 3:
                    issues.append({
                        'issue_type': 'LENGTH_EXPERIENCE_TOO_DETAILED',
                        'location': f'Job: {job_title[:40]}',
                        'description': f'Job from {job_year} ({years_ago} years ago) has {bullet_count} bullets - older roles should have 2-3 bullets',
                        'current': '',
                        'is_highlightable': False,
                        'meta_info': {'bullet_count': bullet_count, 'job_year': job_year, 'years_ago': years_ago},
                    })
        except (ValueError, IndexError):
            continue
    
    return issues


def get_education_detail_issues(structure: CVStructure) -> List[Dict]:
    """
    Check if education section is too detailed for experienced professionals.
    
    Args:
        structure: Parsed CV structure
        
    Returns:
        List of LENGTH_EDUCATION_TOO_DETAILED issues
    """
    issues = []
    
    if not structure.education:
        return issues
    
    education_lines = len([l for l in structure.education.split('\n') if l.strip()])
    
    experience_word_count = 0
    if structure.experience:
        experience_word_count = len(structure.experience.split())
    
    is_experienced = experience_word_count > 200
    
    if is_experienced and education_lines > 6:
        issues.append({
            'issue_type': 'LENGTH_EDUCATION_TOO_DETAILED',
            'location': 'Education Section',
            'description': f'Education section is {education_lines} lines - experienced professionals should keep to 3-4 lines',
            'current': '',
            'is_highlightable': False,
            'meta_info': {'line_count': education_lines},
            'suggestion': 'Focus on degree, institution, and graduation year; remove coursework details',
        })
    
    return issues
