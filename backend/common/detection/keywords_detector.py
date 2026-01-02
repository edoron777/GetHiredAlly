"""
Keywords Detector for CV Optimizer
Detects issues with keyword optimization and ATS compatibility.
"""

import re
from typing import List, Dict, Any, Optional


def detect_keywords_issues(cv_text: str, job_description: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Main function to detect all keyword-related issues.
    
    Args:
        cv_text: Full CV text content
        job_description: Optional job description for keyword matching
        
    Returns:
        List of detected issues
    """
    issues = []
    
    issues.extend(detect_missing_industry_keywords(cv_text, job_description))
    issues.extend(detect_skills_format(cv_text))
    issues.extend(detect_abbreviation_inconsistency(cv_text))
    
    return issues


def detect_missing_industry_keywords(cv_text: str, job_description: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Detect if CV is missing keywords from job description.
    
    Note: This requires job_description parameter to be useful.
    If no job_description provided, skip this detection.
    """
    issues = []
    
    if not job_description:
        return issues
    
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                   'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                   'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                   'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
                   'we', 'you', 'your', 'our', 'their', 'this', 'that', 'these', 'those',
                   'it', 'its', 'they', 'them', 'what', 'which', 'who', 'whom', 'how',
                   'when', 'where', 'why', 'all', 'each', 'every', 'both', 'few', 'more',
                   'most', 'other', 'some', 'such', 'only', 'own', 'same', 'than', 'too',
                   'very', 'just', 'also', 'now', 'here', 'there', 'then', 'once', 'about',
                   'after', 'before', 'between', 'into', 'through', 'during', 'above',
                   'below', 'under', 'over', 'out', 'off', 'down', 'up', 'any', 'not'}
    
    jd_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_description.lower()))
    jd_keywords = jd_words - common_words
    
    cv_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', cv_text.lower()))
    
    missing = jd_keywords - cv_words
    
    jd_lower = job_description.lower()
    important_missing = [kw for kw in missing if jd_lower.count(kw) >= 2]
    
    if len(important_missing) > 5:
        issues.append({
            "issue_type": "KEYWORDS_MISSING_INDUSTRY",
            "location": "Throughout CV",
            "description": f"CV missing {len(important_missing)} keywords from job description",
            "current": ', '.join(sorted(important_missing)[:10]),
            "suggestion": "Add relevant keywords from the job description naturally into your CV"
        })
    
    return issues


def detect_skills_format(cv_text: str) -> List[Dict[str, Any]]:
    """
    Detect if skills are in paragraph format instead of organized list.
    """
    issues = []
    
    skills_match = re.search(
        r'\b(Skills|Technical\s+Skills|Core\s+Competencies)\s*:?\s*\n(.*?)(?=\n[A-Z]|\Z)',
        cv_text,
        re.IGNORECASE | re.DOTALL
    )
    
    if skills_match:
        skills_section = skills_match.group(2)
        
        lines = skills_section.strip().split('\n')
        
        if len(lines) <= 2:
            comma_count = skills_section.count(',')
            if comma_count > 8:
                preview = skills_section[:100] + "..." if len(skills_section) > 100 else skills_section
                issues.append({
                    "issue_type": "KEYWORDS_SKILLS_FORMAT",
                    "location": "Skills section",
                    "description": "Skills listed in paragraph format are harder to scan",
                    "current": preview.strip(),
                    "suggestion": "Organize skills into categories (Programming, Tools, Soft Skills, etc.)"
                })
    
    return issues


def detect_abbreviation_inconsistency(cv_text: str) -> List[Dict[str, Any]]:
    """
    Detect inconsistent use of abbreviations vs full terms.
    """
    issues = []
    
    abbreviation_pairs = [
        ('ML', 'Machine Learning'),
        ('AI', 'Artificial Intelligence'),
        ('NLP', 'Natural Language Processing'),
        ('API', 'Application Programming Interface'),
        ('UI', 'User Interface'),
        ('UX', 'User Experience'),
        ('SQL', 'Structured Query Language'),
        ('JS', 'JavaScript'),
        ('TS', 'TypeScript'),
        ('AWS', 'Amazon Web Services'),
        ('GCP', 'Google Cloud Platform'),
        ('CI/CD', 'Continuous Integration'),
        ('OOP', 'Object-Oriented Programming'),
        ('REST', 'Representational State Transfer'),
        ('HTML', 'HyperText Markup Language'),
        ('CSS', 'Cascading Style Sheets'),
        ('DB', 'Database'),
        ('PM', 'Project Manager'),
        ('QA', 'Quality Assurance'),
        ('SaaS', 'Software as a Service'),
    ]
    
    inconsistencies = []
    
    for abbrev, full in abbreviation_pairs:
        has_abbrev = re.search(r'\b' + re.escape(abbrev) + r'\b', cv_text)
        has_full = re.search(r'\b' + re.escape(full) + r'\b', cv_text, re.IGNORECASE)
        
        if has_abbrev and has_full:
            inconsistencies.append(f"Both '{abbrev}' and '{full}'")
    
    if inconsistencies:
        issues.append({
            "issue_type": "KEYWORDS_ABBREVIATION_INCONSISTENT",
            "location": "Throughout CV",
            "description": "Inconsistent abbreviation usage may confuse ATS",
            "current": ', '.join(inconsistencies[:3]),
            "suggestion": "Use consistent terminology - either abbreviation or full term, not both"
        })
    
    return issues
