"""
Certification Detector

Detects issues related to certifications section.
- Too many certifications (dilutes impact)
- Missing certification details (optional)

DETERMINISTIC: Same text → Same issues (always)
"""

import re
from typing import List, Dict

CERT_THRESHOLD_WARNING = 6
CERT_THRESHOLD_CRITICAL = 9
CERT_IDEAL_MAX = 5
CERT_MAX_ALLOWED = 8

CERT_LINE_PATTERNS = [
    r'^\s*[•\-\*]\s*.*(?:certified|certificate|certification)',
    r'^\s*[•\-\*]\s*.*\((?:aws|gcp|azure|ibm|google|microsoft|oracle|cisco)\)',
    r'^\s*[•\-\*]\s*(?:aws|gcp|azure|ibm|google|microsoft)\s+\w+',
    r'^\s*[•\-\*]\s*.*(?:professional|associate|specialist|expert|master)\s+(?:level|cert)',
    r'^\s*[•\-\*]\s*.*(?:coursera|udemy|linkedin learning|skillup|pluralsight)',
]

CERT_SECTION_HEADERS = [
    'certifications', 'certificates', 'professional certifications',
    'licenses & certifications', 'credentials', 'professional development'
]


def find_certification_section(text: str) -> str:
    """Extract the certifications section from CV."""
    text_lower = text.lower()
    
    for header in CERT_SECTION_HEADERS:
        start_idx = text_lower.find(header)
        if start_idx != -1:
            next_section_headers = [
                'experience', 'education', 'skills', 'projects',
                'awards', 'publications', 'references', 'languages',
                'summary', 'about', 'work history'
            ]
            
            end_idx = len(text)
            search_start = start_idx + len(header)
            
            for next_header in next_section_headers:
                next_idx = text_lower.find(next_header, search_start)
                if next_idx != -1 and next_idx < end_idx:
                    end_idx = next_idx
            
            return text[start_idx:end_idx]
    
    return ""


def count_certifications(text: str) -> int:
    """
    Count the number of certifications in CV.
    Uses multiple heuristics to identify certification lines.
    Enhanced to handle:
    - Sub-categorized certifications (AI & Product Management, Google AI, etc.)
    - Bullet points at various indent levels
    - Parenthetical issuer notations like (IBM), (Google), etc.
    """
    cert_section = find_certification_section(text)
    
    if not cert_section:
        count = 0
        for line in text.split('\n'):
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in [
                'certified', 'certificate', 'certification',
                'coursera', 'udemy', 'linkedin learning',
                '(ibm)', '(google)', '(aws)', '(microsoft)', '(azure)'
            ]):
                count += 1
        return count
    
    lines = cert_section.split('\n')
    cert_count = 0
    
    sub_category_patterns = [
        r'^[A-Z][A-Za-z\s&]+:$',
        r'^[A-Z][A-Za-z\s&]+\s*\(\d+\)$',
        r'^[A-Z][A-Za-z\s&,]+$',
    ]
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        if any(h in line.lower() for h in CERT_SECTION_HEADERS):
            continue
        
        is_subcategory = False
        for pattern in sub_category_patterns:
            if re.match(pattern, line) and len(line) < 50 and '(' not in line.lower()[:20]:
                if any(kw in line.lower() for kw in ['management', 'automation', 'cloud', 'security', 'infrastructure', 'systems', 'analysis', 'ai ', 'google', 'microsoft', 'amazon']):
                    is_subcategory = True
                    break
        
        if is_subcategory:
            continue
        
        if (line.startswith('•') or line.startswith('-') or 
            line.startswith('*') or line.startswith('·') or
            line.startswith('►') or line.startswith('–')):
            cert_count += 1
        elif re.match(r'^\d+\.', line):
            cert_count += 1
        elif re.match(r'^○\s*', line) or re.match(r'^◦\s*', line):
            cert_count += 1
        elif any(indicator in line.lower() for indicator in [
            'certified', 'certificate', 'certification', 
            '(ibm)', '(google)', '(aws)', '(microsoft)', '(azure)',
            '(coursera)', '(udemy)', '(linkedin)', '(meta)', '(cisco)',
            'professional certificate', 'specialization'
        ]):
            cert_count += 1
    
    return cert_count


def detect_certification_count_issues(text: str) -> List[Dict]:
    """
    Detect if CV has too many certifications.
    
    Thresholds:
    - 1-5: Ideal (no issue)
    - 6-8: Warning (consider - getting long)
    - 9+: Critical (important - definitely too many)
    
    Max allowed: 8 certifications
    """
    issues = []
    
    cert_count = count_certifications(text)
    
    if cert_count >= CERT_THRESHOLD_CRITICAL:
        issues.append({
            'issue_type': 'CONTENT_TOO_MANY_CERTIFICATIONS',
            'current': f'{cert_count} certifications listed',
            'match_text': f'{cert_count} certifications listed',
            'suggestion': f'You have {cert_count} certifications listed, but the recommended maximum is {CERT_MAX_ALLOWED}. Consider featuring only the top {CERT_IDEAL_MAX} most relevant ones. Too many certifications dilutes impact and suggests lack of focus. Prioritize certifications that are: (1) directly relevant to your target role, (2) from recognized providers, (3) recently obtained.',
            'severity': 'important',
            'can_auto_fix': False,
            'is_highlightable': False,
            'location': 'Certifications section',
            'details': {
                'certification_count': cert_count,
                'threshold': CERT_THRESHOLD_CRITICAL,
                'max_allowed': CERT_MAX_ALLOWED,
                'recommended_max': CERT_IDEAL_MAX
            }
        })
    elif cert_count >= CERT_THRESHOLD_WARNING:
        issues.append({
            'issue_type': 'CONTENT_TOO_MANY_CERTIFICATIONS',
            'current': f'{cert_count} certifications listed',
            'match_text': f'{cert_count} certifications listed',
            'suggestion': f'You have {cert_count} certifications. The ideal range is 5-8. Consider focusing on the {CERT_IDEAL_MAX} most relevant to your target role for maximum impact.',
            'severity': 'consider',
            'can_auto_fix': False,
            'is_highlightable': False,
            'location': 'Certifications section',
            'details': {
                'certification_count': cert_count,
                'threshold': CERT_THRESHOLD_WARNING,
                'max_allowed': CERT_MAX_ALLOWED,
                'recommended_max': CERT_IDEAL_MAX
            }
        })
    
    return issues


def detect_all_certification_issues(
    text: str,
    cv_block_structure: 'Optional[CVBlockStructure]' = None
) -> List[Dict]:
    """
    Main entry point for certification detection.
    
    Args:
        text: Full CV text
        cv_block_structure: Optional pre-computed CV structure (for efficiency)
    
    DETERMINISTIC: Same text → Same issues (always)
    """
    if cv_block_structure and cv_block_structure.all_certifications:
        cert_count = len(cv_block_structure.all_certifications)
        issues = []
        
        if cert_count >= CERT_THRESHOLD_CRITICAL:
            issues.append({
                'issue_type': 'CONTENT_TOO_MANY_CERTIFICATIONS',
                'current': f'{cert_count} certifications listed',
                'match_text': f'{cert_count} certifications listed',
                'suggestion': f'You have {cert_count} certifications listed, but the recommended maximum is {CERT_MAX_ALLOWED}. Consider featuring only the top {CERT_IDEAL_MAX} most relevant ones. Too many certifications dilutes impact and suggests lack of focus.',
                'severity': 'important',
                'can_auto_fix': False,
                'is_highlightable': False,
                'location': 'Certifications section',
                'details': {
                    'certification_count': cert_count,
                    'threshold': CERT_THRESHOLD_CRITICAL,
                    'max_allowed': CERT_MAX_ALLOWED,
                    'recommended_max': CERT_IDEAL_MAX
                }
            })
        elif cert_count >= CERT_THRESHOLD_WARNING:
            issues.append({
                'issue_type': 'CONTENT_TOO_MANY_CERTIFICATIONS',
                'current': f'{cert_count} certifications listed',
                'match_text': f'{cert_count} certifications listed',
                'suggestion': f'You have {cert_count} certifications. The ideal range is 5-8. Consider focusing on the {CERT_IDEAL_MAX} most relevant.',
                'severity': 'consider',
                'can_auto_fix': False,
                'is_highlightable': False,
                'location': 'Certifications section',
                'details': {
                    'certification_count': cert_count,
                    'threshold': CERT_THRESHOLD_WARNING,
                    'max_allowed': CERT_MAX_ALLOWED,
                    'recommended_max': CERT_IDEAL_MAX
                }
            })
        
        return issues
    
    return detect_certification_count_issues(text)
