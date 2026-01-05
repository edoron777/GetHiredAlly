"""
Abbreviation Consistency Detector

Detects inconsistent use of abbreviations vs full forms.
Rule: Fix the MINORITY form, not all occurrences.

DETERMINISTIC: Same text → Same issues (always)
"""

import re
from typing import List, Dict, Tuple

ABBREVIATION_PAIRS = [
    ('AI', 'Artificial Intelligence'),
    ('ML', 'Machine Learning'),
    ('NLP', 'Natural Language Processing'),
    ('API', 'Application Programming Interface'),
    ('AWS', 'Amazon Web Services'),
    ('GCP', 'Google Cloud Platform'),
    ('UI', 'User Interface'),
    ('UX', 'User Experience'),
    ('CI/CD', 'Continuous Integration/Continuous Deployment'),
    ('CI', 'Continuous Integration'),
    ('CD', 'Continuous Deployment'),
    ('SQL', 'Structured Query Language'),
    ('SaaS', 'Software as a Service'),
    ('PaaS', 'Platform as a Service'),
    ('IaaS', 'Infrastructure as a Service'),
    ('KPI', 'Key Performance Indicator'),
    ('ROI', 'Return on Investment'),
    ('PM', 'Project Manager'),
    ('PM', 'Product Manager'),
    ('QA', 'Quality Assurance'),
    ('DevOps', 'Development Operations'),
    ('IoT', 'Internet of Things'),
    ('VR', 'Virtual Reality'),
    ('AR', 'Augmented Reality'),
]


def count_occurrences(text: str, term: str, case_sensitive: bool = False) -> int:
    """Count occurrences of a term in text."""
    if case_sensitive:
        pattern = r'\b' + re.escape(term) + r'\b'
    else:
        pattern = r'\b' + re.escape(term) + r'\b'
        return len(re.findall(pattern, text, re.IGNORECASE))
    return len(re.findall(pattern, text))


def find_all_positions(text: str, term: str) -> List[Tuple[int, int, str]]:
    """Find all positions of a term in text. Returns (start, end, matched_text)."""
    pattern = r'\b' + re.escape(term) + r'\b'
    matches = []
    for match in re.finditer(pattern, text, re.IGNORECASE):
        matches.append((match.start(), match.end(), match.group()))
    return matches


def detect_abbreviation_issues(text: str) -> List[Dict]:
    """
    Detect inconsistent abbreviation usage.
    
    RULE: If both forms are used, flag the MINORITY form for fixing.
    This allows auto-fix to replace only the minority occurrences.
    """
    issues = []
    
    for abbrev, full_form in ABBREVIATION_PAIRS:
        abbrev_count = count_occurrences(text, abbrev)
        full_count = count_occurrences(text, full_form)
        
        if abbrev_count > 0 and full_count > 0:
            if abbrev_count > full_count:
                minority_term = full_form
                majority_term = abbrev
                minority_count = full_count
                majority_count = abbrev_count
            elif full_count > abbrev_count:
                minority_term = abbrev
                majority_term = full_form
                minority_count = abbrev_count
                majority_count = full_count
            else:
                minority_term = full_form
                majority_term = abbrev
                minority_count = full_count
                majority_count = abbrev_count
            
            positions = find_all_positions(text, minority_term)
            
            issues.append({
                'issue_type': 'FORMAT_INCONSISTENT_ABBREVIATION',
                'match_text': minority_term,
                'suggestion': f"Use '{majority_term}' consistently. Replace {minority_count} occurrence(s) of '{minority_term}' with '{majority_term}'.",
                'can_auto_fix': True,
                'auto_fix_data': {
                    'find': minority_term,
                    'replace': majority_term,
                    'count': minority_count
                },
                'details': {
                    'majority_term': majority_term,
                    'majority_count': majority_count,
                    'minority_term': minority_term,
                    'minority_count': minority_count
                }
            })
    
    return issues


def detect_all_abbreviation_issues(
    text: str,
    cv_block_structure: 'Optional[CVBlockStructure]' = None
) -> List[Dict]:
    """
    Main entry point for abbreviation detection.
    
    Args:
        text: Full CV text
        cv_block_structure: Optional pre-computed CV structure (for efficiency)
    
    DETERMINISTIC: Same text → Same issues (always)
    """
    return detect_abbreviation_issues(text)
