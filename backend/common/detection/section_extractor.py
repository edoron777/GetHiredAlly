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
    
    return structure


def get_section_issues(structure: CVStructure) -> List[Dict]:
    """
    Generate issues based on section analysis.
    
    Returns list of issue dictionaries with issue_type.
    """
    issues = []
    
    if not structure.has_summary:
        issues.append({
            'issue_type': 'CONTENT_GENERIC_STATEMENTS',
            'location': 'Summary Section',
            'description': 'No summary/profile section found',
        })
    elif structure.summary and len(structure.summary.split()) < 30:
        issues.append({
            'issue_type': 'CONTENT_GENERIC_STATEMENTS',
            'location': 'Summary Section',
            'description': f'Summary is too short ({len(structure.summary.split())} words, recommend 30-60)',
            'current': structure.summary[:100] + '...' if len(structure.summary) > 100 else structure.summary,
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
            'current': f'{word_count} words',
        })
    elif word_count < 200:
        issues.append({
            'issue_type': 'LENGTH_CV_TOO_SHORT',
            'location': 'Overall CV',
            'description': f'CV is only {word_count} words - consider adding more detail',
            'current': f'{word_count} words',
        })
    
    return issues
