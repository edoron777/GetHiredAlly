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
    'licenses & certifications', 'licenses and certifications',
    'certifications & licenses', 'certifications and licenses',
    'credentials', 'professional development',
    'training & certifications', 'training and certifications',
    'courses & certifications', 'courses and certifications',
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
    - Lines with years in parentheses like "AWS Solutions Architect (2023)"
    - Non-bulleted certification lists
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
    
    sub_category_keywords = [
        'management', 'automation', 'cloud computing', 'security', 
        'infrastructure', 'systems', 'analysis', 'google ai', 
        'microsoft azure', 'amazon web'
    ]
    
    cert_indicators = [
        'certified', 'certificate', 'certification', 
        '(ibm)', '(google)', '(aws)', '(microsoft)', '(azure)',
        '(coursera)', '(udemy)', '(linkedin)', '(meta)', '(cisco)',
        '(oracle)', '(vmware)', '(salesforce)', '(comptia)',
        'professional certificate', 'specialization',
        'associate', 'professional', 'expert', 'practitioner',
        'foundational', 'specialty', 'solutions architect'
    ]
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        if any(h in line.lower() for h in CERT_SECTION_HEADERS):
            continue
        
        if len(line) < 5:
            continue
            
        is_subcategory = False
        if line.endswith(':') and len(line) < 40:
            line_lower = line.lower()
            if any(kw in line_lower for kw in sub_category_keywords):
                is_subcategory = True
        
        if is_subcategory:
            continue
        
        is_cert = False
        
        if (line.startswith('•') or line.startswith('-') or 
            line.startswith('*') or line.startswith('·') or
            line.startswith('►') or line.startswith('–') or
            line.startswith('○') or line.startswith('◦')):
            is_cert = True
        elif re.match(r'^\d+[.)]\s*', line):
            is_cert = True
        elif re.search(r'\(\d{4}\)', line):
            is_cert = True
        elif any(indicator in line.lower() for indicator in cert_indicators):
            is_cert = True
        elif len(line) > 10 and not line.endswith(':'):
            is_cert = True
            
        if is_cert:
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
    
    Note: Always uses text-based counting (count_certifications) as it's more
    accurate than block-based extraction for counting purposes. Block-based
    extraction may miss certifications that don't match specific patterns.
    """
    return detect_certification_count_issues(text)
