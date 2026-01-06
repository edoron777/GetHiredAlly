"""
CV Section Extractor

Multi-pass section detection for robust CV parsing.
Handles CVs with and without explicit section headers.
100% CODE - No AI - Deterministic results.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

JOB_TITLE_PATTERNS = [
    r'\b(VP|Vice President|Director|Manager|Lead|Head|Chief|Senior|Junior|'
    r'Engineer|Developer|Architect|Analyst|Consultant|Specialist|Coordinator|'
    r'Administrator|Executive|Officer|President|Founder|Co-Founder|Partner|'
    r'Associate|Assistant|Intern|Trainee|Supervisor|Team Lead|Tech Lead|'
    r'Principal|Staff|Distinguished|Fellow)\b',
]

DATE_PATTERNS = [
    r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
    r'Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|'
    r'Dec(?:ember)?)\s*\.?\s*\d{4}\s*[-–—]\s*(?:Present|Current|Now|'
    r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
    r'Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|'
    r'Dec(?:ember)?)\s*\.?\s*\d{4})',
    r'\b(19|20)\d{2}\s*[-–—]\s*(?:Present|Current|Now|(19|20)\d{2})\b',
    r'\b\d{1,2}/\d{4}\s*[-–—]\s*(?:Present|Current|Now|\d{1,2}/\d{4})\b',
]

KNOWN_COMPANIES = [
    'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Facebook', 'Netflix',
    'IBM', 'Oracle', 'Salesforce', 'Adobe', 'Intel', 'Cisco', 'SAP',
    'Deloitte', 'McKinsey', 'BCG', 'Bain', 'Accenture', 'PwC', 'EY', 'KPMG',
    'Goldman Sachs', 'Morgan Stanley', 'JPMorgan', 'Citi', 'Bank of America',
    'Tesla', 'SpaceX', 'Uber', 'Airbnb', 'Twitter', 'LinkedIn', 'Stripe',
    'Palantir', 'Snowflake', 'Databricks', 'Confluent', 'HashiCorp',
    'SanDisk', 'Western Digital', 'Seagate', 'Dell', 'HP', 'Lenovo',
]

EDUCATION_PATTERNS = [
    r'\b(University|College|Institute|School|Academy|Bachelor|Master|PhD|'
    r'MBA|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|Ph\.?D\.?|Degree|Diploma|'
    r'Certificate|Certification|Graduated|GPA|Major|Minor)\b',
]

CONTACT_PATTERNS = {
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'phone': r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    'linkedin': r'linkedin\.com/in/[\w-]+',
    'github': r'github\.com/[\w-]+',
}

SUMMARY_HEADERS = [
    'summary', 'professional summary', 'executive summary',
    'profile', 'professional profile', 'career profile',
    'objective', 'career objective', 'job objective',
    'about', 'about me', 'introduction', 'overview',
]

EXPERIENCE_HEADERS = [
    'experience', 'work experience', 'professional experience',
    'employment', 'employment history', 'work history',
    'career history', 'positions held', 'roles',
]

EDUCATION_HEADERS = [
    'education', 'academic background', 'educational background',
    'qualifications', 'academic qualifications', 'degrees',
]

SKILLS_HEADERS = [
    'skills', 'technical skills', 'core competencies',
    'key skills', 'expertise', 'technologies', 'tools',
    'proficiencies', 'capabilities', 'competencies',
]

CERTIFICATIONS_HEADERS = [
    'certifications', 'certificates', 'licenses',
    'professional certifications', 'credentials',
    'accreditations', 'training',
]

# Sub-categories that should NOT start new sections
# These appear WITHIN sections (like certification categories within CERTIFICATIONS)
SUB_CATEGORY_PATTERNS = [
    # Certification sub-categories
    'ai & product management',
    'google ai certifications', 
    'microsoft cloud & security',
    'microsoft cloud security',
    'microsoft infrastructure',
    'security & compliance',
    'security compliance',
    'systems & business analysis',
    'systems business analysis',
    'cloud certifications',
    'security certifications',
    'management certifications',
    
    # Experience sub-headers (within a job)
    'technology research',
    'ai security projects',
    'identity infrastructure', 
    'delivery excellence',
    'technology domains',
    'responsibilities',
    'achievements',
    'key accomplishments',
    'key achievements',
    'core responsibilities',
    
    # Skills sub-categories
    'programming languages',
    'frameworks',
    'tools',
    'databases',
    'cloud platforms',
    'methodologies',
]

def _is_sub_category(text: str) -> bool:
    """Check if text is a sub-category (should NOT start new section)."""
    cleaned = text.lower().strip()
    # Remove formatting markers
    cleaned = cleaned.replace('[h1]', '').replace('[h2]', '').replace('[bold]', '')
    cleaned = cleaned.replace('**', '').replace('*', '').strip(':').strip()
    
    for pattern in SUB_CATEGORY_PATTERNS:
        if pattern in cleaned or cleaned == pattern:
            return True
    return False


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
    
    contact: Optional[str] = None
    summary: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None
    certifications: Optional[str] = None
    
    has_contact: bool = False
    has_summary: bool = False
    has_experience: bool = False
    has_education: bool = False
    has_skills: bool = False
    has_certifications: bool = False
    
    section_order: List[str] = field(default_factory=list)
    section_boundaries: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    detection_method: Dict[str, str] = field(default_factory=dict)
    job_entries: List[Tuple[int, int]] = field(default_factory=list)


def _normalize_header(text: str) -> str:
    """Normalize header text for comparison."""
    return re.sub(r'[^a-z\s]', '', text.lower()).strip()


def _is_section_header(line: str) -> Tuple[bool, Optional[str]]:
    """Check if line is a section header. Returns (is_header, section_type).
    
    IMPORTANT: Sub-categories (like "AI & Product Management" within Certifications)
    are NOT section headers and should return False.
    """
    normalized = _normalize_header(line)
    
    if not normalized or len(normalized) > 50:
        return False, None
    
    # CRITICAL: Check if this is a sub-category first - these are NOT section headers
    if _is_sub_category(line):
        logger.debug(f"[SECTION_HEADER] Skipping sub-category: {line.strip()[:50]}")
        return False, None
    
    for header in SUMMARY_HEADERS:
        if normalized == header or normalized.startswith(header + ' '):
            return True, 'summary'
    
    for header in EXPERIENCE_HEADERS:
        if normalized == header or normalized.startswith(header + ' '):
            return True, 'experience'
    
    for header in EDUCATION_HEADERS:
        if normalized == header or normalized.startswith(header + ' '):
            return True, 'education'
    
    for header in SKILLS_HEADERS:
        if normalized == header or normalized.startswith(header + ' '):
            return True, 'skills'
    
    for header in CERTIFICATIONS_HEADERS:
        if normalized == header or normalized.startswith(header + ' '):
            return True, 'certifications'
    
    return False, None


def _detect_job_entry_start(line: str, next_lines: List[str]) -> bool:
    """
    Detect if this line starts a job entry.
    
    Requirements for job entry detection:
    - Must have date pattern (e.g., "Jul 2020 - Present") on current line OR next few lines
    - Must have company name OR job title
    - Company name alone is NOT enough (prevents false positives like "worked at Citi, Microsoft...")
    """
    line_stripped = line.strip()
    if not line_stripped:
        return False
    
    has_company = any(company.lower() in line_stripped.lower() for company in KNOWN_COMPANIES)
    has_title = any(re.search(p, line_stripped, re.IGNORECASE) for p in JOB_TITLE_PATTERNS)
    has_date = any(re.search(p, line_stripped, re.IGNORECASE) for p in DATE_PATTERNS)
    
    if has_date and (has_company or has_title):
        return True
    
    if len(line_stripped) > 100:
        return False
    
    if (has_company or has_title) and line_stripped and line_stripped[0].isupper():
        upcoming_text = ' '.join(next_lines[:3])
        has_date_nearby = any(re.search(p, upcoming_text, re.IGNORECASE) for p in DATE_PATTERNS)
        
        if has_date_nearby:
            return True
    
    return False


def _extract_contact_section(lines: List[str]) -> Tuple[Optional[str], int]:
    """Extract contact info from first lines. Returns (contact_text, end_line)."""
    contact_lines = []
    contact_end = 0
    
    for i, line in enumerate(lines[:12]):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        has_email = re.search(CONTACT_PATTERNS['email'], line)
        has_phone = re.search(CONTACT_PATTERNS['phone'], line)
        has_linkedin = re.search(CONTACT_PATTERNS['linkedin'], line)
        has_github = re.search(CONTACT_PATTERNS['github'], line)
        
        if i == 0:
            contact_lines.append(line_stripped)
            contact_end = i
            continue
        
        if has_email or has_phone or has_linkedin or has_github:
            contact_lines.append(line_stripped)
            contact_end = i
            continue
        
        is_header, _ = _is_section_header(line)
        if is_header:
            break
        
        if len(line_stripped) < 150 and '|' in line_stripped:
            contact_lines.append(line_stripped)
            contact_end = i
            continue
        
        if _detect_job_entry_start(line_stripped, [l.strip() for l in lines[i+1:i+5]]):
            break
        
        if len(line_stripped) > 200:
            break
    
    if contact_lines:
        return '\n'.join(contact_lines), contact_end
    return None, 0


def _detect_job_entries(lines: List[str], start_from: int, header_lines: set) -> List[Tuple[int, int]]:
    """Detect job entries by pattern when no Experience header exists."""
    job_entries = []
    current_job_start = None
    
    for i in range(start_from + 1, len(lines)):
        line = lines[i].strip()
        
        if not line:
            continue
        
        if i in header_lines:
            if current_job_start is not None:
                job_entries.append((current_job_start, i - 1))
                current_job_start = None
            break
        
        remaining_lines = [l.strip() for l in lines[i+1:i+6]]
        if _detect_job_entry_start(line, remaining_lines):
            if current_job_start is not None:
                job_entries.append((current_job_start, i - 1))
            current_job_start = i
    
    if current_job_start is not None:
        end_line = len(lines) - 1
        for hl in sorted(header_lines):
            if hl > current_job_start:
                end_line = hl - 1
                break
        job_entries.append((current_job_start, end_line))
    
    return job_entries


def extract_sections(text: str) -> CVStructure:
    """
    Extract sections from CV text using multi-pass detection.
    
    PASS 1: Extract contact info from first few lines
    PASS 2: Find explicit section headers
    PASS 3: Detect implicit sections (jobs without Experience header)
    PASS 4: Assign content to sections
    """
    structure = CVStructure(raw_text=text)
    lines = text.split('\n')
    
    logger.debug(f"[SECTION PARSER] Starting extraction, {len(lines)} lines")
    
    contact_text, contact_end = _extract_contact_section(lines)
    if contact_text:
        structure.contact = contact_text
        structure.has_contact = True
        structure.detection_method['contact'] = 'pattern'
        logger.debug(f"[SECTION PARSER] Pass 1: Contact ends at line {contact_end}")
    
    headers_found = []
    
    for i, line in enumerate(lines):
        if i <= contact_end:
            continue
        
        is_header, section_type = _is_section_header(line)
        if is_header and section_type:
            headers_found.append((i, section_type, line.strip()))
            logger.debug(f"[SECTION PARSER] Pass 2: Found '{section_type}' header at line {i}")
    
    experience_header_found = any(h[1] == 'experience' for h in headers_found)
    job_entries = []
    
    if not experience_header_found:
        logger.debug("[SECTION PARSER] Pass 3: No Experience header, detecting job entries")
        header_lines = {h[0] for h in headers_found}
        
        summary_end = contact_end
        for h in headers_found:
            if h[1] == 'summary':
                for j in range(h[0] + 1, len(lines)):
                    is_next_header, _ = _is_section_header(lines[j])
                    if is_next_header or _detect_job_entry_start(lines[j].strip(), [l.strip() for l in lines[j+1:j+5]]):
                        summary_end = j - 1
                        break
                else:
                    summary_end = len(lines) - 1
                break
        
        job_entries = _detect_job_entries(lines, summary_end, header_lines)
        logger.debug(f"[SECTION PARSER] Pass 3: Found {len(job_entries)} job entries")
    
    headers_sorted = sorted(headers_found, key=lambda x: x[0])
    
    for idx, (line_idx, section_type, header_text) in enumerate(headers_sorted):
        start = line_idx + 1
        
        if idx + 1 < len(headers_sorted):
            end = headers_sorted[idx + 1][0] - 1
        else:
            end = len(lines) - 1
        
        # ENHANCED: For summary section, detect if job entries appear BEFORE the next header
        # This catches cases where jobs (like Citi) appear in summary content
        if section_type == 'summary':
            # First check existing job_entries (from Pass 3)
            if job_entries:
                first_job = job_entries[0][0] if job_entries else end
                end = min(end, first_job - 1)
            else:
                # Also scan for job entries within the summary content
                # This handles cases where Experience header exists but jobs appear in summary
                for scan_line in range(start, end + 1):
                    if scan_line < len(lines):
                        remaining = [l.strip() for l in lines[scan_line+1:scan_line+6]] if scan_line+1 < len(lines) else []
                        if _detect_job_entry_start(lines[scan_line].strip(), remaining):
                            logger.debug(f"[SECTION_PARSER] Job entry detected at line {scan_line} within summary, adjusting end")
                            end = scan_line - 1
                            break
        
        content = '\n'.join(lines[start:end + 1]).strip()
        
        structure.section_boundaries[section_type] = (start, end)
        structure.detection_method[section_type] = 'header'
        
        if section_type == 'summary':
            structure.summary = content
            structure.has_summary = True
            if 'summary' not in structure.section_order:
                structure.section_order.append('summary')
        elif section_type == 'experience':
            # ENHANCED: Check if there are job entries that start BEFORE this experience header
            # If so, extend the experience section to include them
            experience_start = start
            for scan_back in range(line_idx - 1, contact_end, -1):
                if scan_back >= 0 and scan_back < len(lines):
                    remaining = [l.strip() for l in lines[scan_back+1:scan_back+6]] if scan_back+1 < len(lines) else []
                    if _detect_job_entry_start(lines[scan_back].strip(), remaining):
                        experience_start = scan_back
                        logger.debug(f"[SECTION_PARSER] Extended experience start from {start} to {experience_start}")
                        break
            
            if experience_start < start:
                content = '\n'.join(lines[experience_start:end + 1]).strip()
                structure.section_boundaries[section_type] = (experience_start, end)
            
            structure.experience = content
            structure.has_experience = True
            if 'experience' not in structure.section_order:
                structure.section_order.append('experience')
        elif section_type == 'education':
            structure.education = content
            structure.has_education = True
            if 'education' not in structure.section_order:
                structure.section_order.append('education')
        elif section_type == 'skills':
            structure.skills = content
            structure.has_skills = True
            if 'skills' not in structure.section_order:
                structure.section_order.append('skills')
        elif section_type == 'certifications':
            structure.certifications = content
            structure.has_certifications = True
            if 'certifications' not in structure.section_order:
                structure.section_order.append('certifications')
        
        section = CVSection(
            name=section_type,
            header=header_text,
            content=content,
            start_pos=sum(len(l) + 1 for l in lines[:start]),
            end_pos=sum(len(l) + 1 for l in lines[:end + 1]),
            line_number=line_idx + 1,
        )
        structure.sections.append(section)
    
    if job_entries and not structure.has_experience:
        start_line = job_entries[0][0]
        end_line = job_entries[-1][1]
        
        for h in headers_sorted:
            if h[0] > start_line:
                end_line = min(end_line, h[0] - 1)
                break
        
        experience_content = '\n'.join(lines[start_line:end_line + 1]).strip()
        
        if len(experience_content) > 100:
            structure.experience = experience_content
            structure.has_experience = True
            structure.section_boundaries['experience'] = (start_line, end_line)
            structure.detection_method['experience'] = 'pattern'
            structure.job_entries = job_entries
            
            if 'experience' not in structure.section_order:
                insert_pos = 1 if structure.has_summary else 0
                structure.section_order.insert(insert_pos, 'experience')
            
            logger.debug(f"[SECTION PARSER] Experience from patterns: {len(experience_content)} chars")
    
    if not structure.has_experience:
        fallback = _extract_experience_by_pattern(text)
        if fallback:
            structure.experience = fallback
            structure.has_experience = True
            structure.detection_method['experience'] = 'legacy_fallback'
            if 'experience' not in structure.section_order:
                structure.section_order.append('experience')
    
    logger.info(f"[SECTION PARSER] Complete: summary={len(structure.summary or '')} chars, "
                f"experience={len(structure.experience or '')} chars, "
                f"education={len(structure.education or '')} chars, "
                f"skills={len(structure.skills or '')} chars")
    
    return structure


def _extract_experience_by_pattern(text: str) -> Optional[str]:
    """Legacy fallback: Extract experience by detecting employment patterns."""
    employment_date_pattern = re.compile(
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[-–]\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
        re.IGNORECASE
    )
    
    year_range_pattern = re.compile(r'\b(19|20)\d{2}\s*[-–]\s*(Present|(19|20)\d{2})\b', re.IGNORECASE)
    
    job_title_pattern = re.compile(
        r'\b(?:\*{0,2})(VP|Director|Manager|Engineer|Lead|Analyst|Specialist|'
        r'Consultant|Developer|Architect|Officer|Head|Chief|Coordinator|'
        r'Administrator|Executive|President|Advisor|Senior|Associate)(?:\*{0,2})\b',
        re.IGNORECASE
    )
    
    lines = text.split('\n')
    experience_lines = []
    in_experience = False
    
    stop_headers = ['education', 'certifications', 'skills', 'references', 'hobbies', 'interests', 'awards', 'languages']
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        line_clean = re.sub(r'[#*_]', '', line_lower)
        
        if any(header in line_clean for header in stop_headers) and len(line.strip()) < 50:
            if in_experience and len(experience_lines) > 5:
                break
        
        has_date = employment_date_pattern.search(line) or year_range_pattern.search(line)
        has_title = job_title_pattern.search(line)
        
        if has_date or (has_title and not in_experience and i > 10):
            if not in_experience:
                in_experience = True
                for prev_line in lines[max(0, i-3):i]:
                    if prev_line.strip():
                        experience_lines.append(prev_line)
            experience_lines.append(line)
        elif in_experience:
            experience_lines.append(line)
    
    if experience_lines and len('\n'.join(experience_lines)) > 200:
        return '\n'.join(experience_lines).strip()
    return None


def get_section_issues(structure: CVStructure) -> List[Dict]:
    """Generate issues based on section analysis."""
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
    """Check if old jobs have too much detail."""
    import datetime
    issues = []
    current_year = datetime.datetime.now().year
    
    job_section_pattern = re.compile(
        r'^([A-Z][a-zA-Z\s,]+)\s*[-–|]\s*.*?((?:19|20)\d{2})',
        re.MULTILINE
    )
    
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
    """Check if education section is too detailed for experienced professionals."""
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
