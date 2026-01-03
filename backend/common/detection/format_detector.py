"""
Format and Consistency Detector

Detects formatting inconsistencies using pattern matching.
100% CODE - No AI - Deterministic results.
"""

import re
from typing import List, Dict, Set
from collections import Counter


DATE_FORMATS = {
    'month_year_full': re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', re.IGNORECASE),
    'month_year_abbr': re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[.]?\s+\d{4}\b', re.IGNORECASE),
    'mm_yyyy': re.compile(r'\b(?:0?[1-9]|1[0-2])/\d{4}\b'),
    'mm_yy': re.compile(r'\b(?:0?[1-9]|1[0-2])/\d{2}\b'),
    'yyyy_mm': re.compile(r'\b\d{4}[-/](?:0?[1-9]|1[0-2])\b'),
    'year_only': re.compile(r'\b(?:19|20)\d{2}\b'),
}

BULLET_STYLES = {
    'dash': re.compile(r'^\s*-\s+', re.MULTILINE),
    'bullet': re.compile(r'^\s*•\s*', re.MULTILINE),
    'asterisk': re.compile(r'^\s*\*\s+', re.MULTILINE),
    'arrow': re.compile(r'^\s*>\s+', re.MULTILINE),
    'number': re.compile(r'^\s*\d+[.)]\s+', re.MULTILINE),
}

REQUIRED_SECTIONS = ['experience', 'education', 'skills']

SECTION_HEADER_PATTERNS = [
    re.compile(r'^[A-Z][A-Z\s]{2,}$', re.MULTILINE),
    re.compile(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*:$', re.MULTILINE),
    re.compile(r'^\*\*[A-Za-z\s]+\*\*$', re.MULTILINE),
    re.compile(r'^__[A-Za-z\s]+__$', re.MULTILINE),
]

SPECIAL_CHARACTERS = {
    'smart_quotes': ['"', '"', ''', '''],
    'dashes': ['—', '–'],
    'bullets': ['●', '○', '■', '□', '►', '▪', '◆', '◇'],
    'other': ['…', '™', '®', '©', '°', '±', '×', '÷'],
}

TABLE_PATTERNS = [
    re.compile(r'\t.*\t.*\t'),
    re.compile(r'\|.*\|.*\|'),
]

NONSTANDARD_HEADERS = [
    'career journey', 'my journey', 'journey',
    'what i do', 'about me',
    'my story', 'bio',
    'toolkit', 'arsenal', 'tech stack',
    'learning', 'studies', 'schooling',
]


def detect_date_inconsistency(text: str) -> List[Dict]:
    """
    Detect inconsistent date formats.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of DATE_FORMAT_INCONSISTENT issues
    """
    issues = []
    formats_found = {}
    
    for format_name, pattern in DATE_FORMATS.items():
        matches = pattern.findall(text)
        if matches:
            formats_found[format_name] = matches
    
    if len(formats_found) > 1:
        examples = []
        for fmt, matches in formats_found.items():
            examples.append(matches[0])
        
        first_example = examples[0] if examples else ''
        
        issues.append({
            'issue_type': 'FORMAT_INCONSISTENT_DATES',
            'location': 'Throughout CV',
            'description': f'Multiple date formats used ({len(formats_found)} different formats)',
            'current': first_example,
            'is_highlightable': bool(first_example and first_example in text),
            'all_instances': examples[:5],
            'suggestion': 'Use a consistent date format throughout (e.g., "Jan 2020" or "January 2020")',
        })
    
    return issues


def detect_bullet_inconsistency(text: str) -> List[Dict]:
    """
    Detect inconsistent bullet point styles.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of FORMAT_INCONSISTENT issues
    """
    issues = []
    styles_found = {}
    
    for style_name, pattern in BULLET_STYLES.items():
        matches = pattern.findall(text)
        if matches:
            styles_found[style_name] = len(matches)
    
    if len(styles_found) > 1:
        issues.append({
            'issue_type': 'FORMAT_INCONSISTENT_BULLETS',
            'location': 'Bullet Points',
            'description': f'Inconsistent bullet styles ({len(styles_found)} different styles: {", ".join(styles_found.keys())})',
            'current': '',
            'is_highlightable': False,
            'meta_info': ', '.join(styles_found.keys()),
            'suggestion': 'Use a consistent bullet style throughout',
        })
    
    return issues


def detect_whitespace_issues(text: str) -> List[Dict]:
    """
    Detect whitespace problems.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of WHITESPACE_ISSUE issues
    """
    issues = []
    
    if re.search(r'\n{4,}', text):
        issues.append({
            'issue_type': 'FORMAT_EXCESSIVE_BLANK_LINES',
            'location': 'Throughout CV',
            'description': 'Excessive blank lines detected',
            'current': '',
            'is_highlightable': False,
            'suggestion': 'Remove extra blank lines for cleaner appearance',
        })
    
    trailing_matches = list(re.finditer(r'[ \t]+$', text, re.MULTILINE))
    trailing_count = len(trailing_matches)
    if trailing_count > 5:
        issues.append({
            'issue_type': 'FORMAT_TRAILING_WHITESPACE',
            'location': 'Throughout CV',
            'description': f'Trailing whitespace on {trailing_count} lines',
            'current': '',
            'is_highlightable': False,
            'meta_info': f'{trailing_count} lines affected',
            'suggestion': 'Remove trailing spaces for cleaner formatting',
        })
    
    indents = re.findall(r'^[ \t]+', text, re.MULTILINE)
    if indents:
        indent_sizes = [len(i.replace('\t', '    ')) for i in indents]
        unique_indents = len(set(indent_sizes))
        
        if unique_indents > 3:
            issues.append({
                'issue_type': 'FORMAT_INCONSISTENT_SPACING',
                'location': 'Indentation',
                'description': f'Inconsistent indentation ({unique_indents} different levels)',
                'current': '',
                'is_highlightable': False,
                'suggestion': 'Use consistent indentation throughout',
            })
    
    return issues


def detect_missing_section_headers(text: str) -> List[Dict]:
    """
    Detect if CV lacks clear section headers.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of FORMAT_MISSING_SECTION_HEADERS issues
    """
    issues = []
    text_lower = text.lower()
    lines = text.split('\n')
    
    missing_sections = []
    
    for section in REQUIRED_SECTIONS:
        section_found_as_header = False
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            if section not in line_lower:
                continue
            
            if line_stripped.isupper() and len(line_stripped) >= 3:
                section_found_as_header = True
                break
            
            if line_stripped.endswith(':'):
                section_found_as_header = True
                break
            
            if line_stripped.startswith('**') and line_stripped.endswith('**'):
                section_found_as_header = True
                break
            
            if line_stripped.startswith('__') and line_stripped.endswith('__'):
                section_found_as_header = True
                break
            
            words = line_stripped.split()
            if len(words) <= 3 and words and words[0][0].isupper():
                section_found_as_header = True
                break
        
        if not section_found_as_header:
            missing_sections.append(section.title())
    
    if len(missing_sections) >= 2:
        issues.append({
            'issue_type': 'FORMAT_MISSING_SECTION_HEADERS',
            'location': 'CV Structure',
            'description': f'Missing clear section headers: {", ".join(missing_sections)}',
            'current': '',
            'is_highlightable': False,
            'meta_info': ', '.join(missing_sections),
            'suggestion': 'Add clear section headers like EXPERIENCE, EDUCATION, SKILLS in all caps or title case',
        })
    
    return issues


def detect_multiple_spaces(text: str) -> List[Dict]:
    """
    Detect multiple consecutive spaces in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of FORMAT_MULTIPLE_SPACES issues
    """
    issues = []
    
    lines = text.split('\n')
    double_space_count = 0
    
    for line in lines:
        stripped = line.lstrip()
        matches = re.findall(r'  +', stripped)
        double_space_count += len(matches)
    
    if double_space_count > 5:
        spaces_match = re.search(r'\S(  +)\S', text)
        current_text = ''
        if spaces_match:
            start = max(0, spaces_match.start() - 10)
            end = min(len(text), spaces_match.end() + 10)
            current_text = text[start:end].strip()
        
        issues.append({
            'issue_type': 'FORMAT_MULTIPLE_SPACES',
            'location': 'Throughout CV',
            'description': f'Multiple consecutive spaces found ({double_space_count} instances)',
            'current': current_text,
            'is_highlightable': bool(current_text),
            'suggestion': 'Replace multiple spaces with single spaces',
        })
    
    return issues


def detect_tables(text: str) -> List[Dict]:
    """
    Detect table structures that cause ATS issues.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of FORMAT_TABLES_DETECTED issues
    """
    issues = []
    
    for pattern in TABLE_PATTERNS:
        match = pattern.search(text)
        if match:
            table_text = match.group(0)[:50] if len(match.group(0)) > 50 else match.group(0)
            issues.append({
                'issue_type': 'FORMAT_TABLES_DETECTED',
                'location': 'CV Layout',
                'description': 'Table structure detected - many ATS systems cannot parse tables correctly',
                'current': table_text.strip(),
                'is_highlightable': True,
                'suggestion': 'Convert table content to simple bullet points',
            })
            break
    
    return issues


def detect_multiple_columns(text: str) -> List[Dict]:
    """
    Detect multi-column layouts.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of FORMAT_MULTIPLE_COLUMNS issues
    """
    issues = []
    lines = text.split('\n')
    
    short_content_lines = 0
    total_content_lines = 0
    
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped) > 3:
            total_content_lines += 1
            if len(stripped) < 30:
                short_content_lines += 1
    
    mid_line_tabs = len(re.findall(r'[^\t\n]\t+[^\t\n]', text))
    
    if total_content_lines > 10:
        short_ratio = short_content_lines / total_content_lines
        if short_ratio > 0.3 or mid_line_tabs > 10:
            issues.append({
                'issue_type': 'FORMAT_MULTIPLE_COLUMNS',
                'location': 'CV Layout',
                'description': 'Multi-column layout detected - ATS may read columns incorrectly',
                'current': '',
                'is_highlightable': False,
                'suggestion': 'Use single-column format for better ATS compatibility',
            })
    
    return issues


def detect_special_characters(text: str) -> List[Dict]:
    """
    Detect non-standard characters that cause ATS issues.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of FORMAT_SPECIAL_CHARACTERS issues
    """
    issues = []
    found_chars = []
    
    for category, chars in SPECIAL_CHARACTERS.items():
        for char in chars:
            if char in text:
                found_chars.append(char)
    
    if found_chars:
        first_char = found_chars[0] if found_chars else ''
        char_in_text = first_char in text if first_char else False
        
        issues.append({
            'issue_type': 'FORMAT_SPECIAL_CHARACTERS',
            'location': 'Throughout CV',
            'description': f'Special characters found that may cause ATS issues: {" ".join(found_chars[:5])}',
            'current': first_char,
            'is_highlightable': char_in_text,
            'all_instances': found_chars[:10],
            'suggestion': 'Replace with standard ASCII characters (e.g., straight quotes, regular dashes)',
        })
    
    return issues


def detect_footer_content(cv_text: str) -> List[Dict]:
    """
    Detect if important content appears in footer area.
    
    ATS systems typically skip header and footer content.
    
    Args:
        cv_text: Full CV text
        
    Returns:
        List of FORMAT_CONTENT_IN_FOOTER issues
    """
    issues = []
    lines = cv_text.strip().split('\n')
    
    if len(lines) < 5:
        return issues
    
    footer_lines = lines[-3:]
    footer_text = '\n'.join(footer_lines).lower()
    
    footer_patterns = [
        r'page\s*\d+\s*(of\s*\d+)?',
        r'[\w.]+@[\w.]+\.\w+',
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        r'linkedin\.com',
    ]
    
    for pattern in footer_patterns:
        if re.search(pattern, footer_text):
            if re.search(r'@|linkedin|phone|\d{3}[-.\s]?\d{3}', footer_text):
                issues.append({
                    'issue_type': 'FORMAT_CONTENT_IN_FOOTER',
                    'location': 'Document Footer',
                    'description': 'Contact information detected in footer area. ATS systems typically skip footers.',
                    'current': footer_lines[-1].strip() if footer_lines else '',
                    'is_highlightable': True,
                })
                break
    
    return issues


def detect_nonstandard_headers(cv_text: str) -> List[Dict]:
    """
    Detect creative/non-standard section headers that ATS may not recognize.
    
    Args:
        cv_text: Full CV text
        
    Returns:
        List of FORMAT_NONSTANDARD_HEADERS issues
    """
    issues = []
    lines = cv_text.split('\n')
    found_headers = set()
    
    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        if len(line_stripped) < 30 and line_stripped:
            for nonstandard in NONSTANDARD_HEADERS:
                if nonstandard in line_lower and nonstandard not in found_headers:
                    found_headers.add(nonstandard)
                    issues.append({
                        'issue_type': 'FORMAT_NONSTANDARD_HEADERS',
                        'location': 'Section Headers',
                        'description': f'Non-standard section header detected. ATS may not recognize creative headers.',
                        'current': line_stripped,
                        'is_highlightable': True,
                    })
                    break
    
    return issues


def detect_skills_format_issues(text: str) -> List[Dict]:
    """
    Detect if skills are written as paragraphs instead of lists.
    
    ATS systems often fail to parse skills in paragraph format.
    
    Args:
        text: Full CV text
        
    Returns:
        List of FORMAT_SKILLS_IN_PARAGRAPH issues
    """
    issues = []
    
    skills_match = re.search(
        r'(?i)(skills|technical skills|competencies)[:\s]*\n(.*?)(?=\n\s*\n|\n[A-Z]|\Z)',
        text,
        re.DOTALL
    )
    
    if skills_match:
        skills_content = skills_match.group(2).strip()
        
        lines = skills_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if len(line) > 50 and not re.match(r'^[\•\-\*\●\►]', line):
                if line.count(',') >= 3:
                    issues.append({
                        'issue_type': 'FORMAT_SKILLS_IN_PARAGRAPH',
                        'location': 'Skills Section',
                        'description': 'Skills written as comma-separated paragraph instead of list format.',
                        'current': line[:100] + '...' if len(line) > 100 else line,
                        'is_highlightable': True,
                    })
                    break
    
    return issues


def detect_format_issues(text: str) -> List[Dict]:
    """
    Detect all formatting issues.
    
    This is the MAIN function for format analysis.
    100% deterministic - same text → same result.
    
    Args:
        text: Full CV text
        
    Returns:
        List of formatting issues
    """
    issues = []
    
    issues.extend(detect_date_inconsistency(text))
    issues.extend(detect_bullet_inconsistency(text))
    issues.extend(detect_whitespace_issues(text))
    issues.extend(detect_missing_section_headers(text))
    issues.extend(detect_multiple_spaces(text))
    issues.extend(detect_tables(text))
    issues.extend(detect_multiple_columns(text))
    issues.extend(detect_special_characters(text))
    issues.extend(detect_footer_content(text))
    issues.extend(detect_nonstandard_headers(text))
    issues.extend(detect_skills_format_issues(text))
    
    return issues
