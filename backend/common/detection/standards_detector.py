"""
Standards Detector for CV Optimizer
Detects issues with professional standards and best practices.
"""

import re
from typing import List, Dict, Any


def detect_standards_issues(cv_text: str) -> List[Dict[str, Any]]:
    """
    Main function to detect all standards-related issues.
    
    Args:
        cv_text: Full CV text content
        
    Returns:
        List of detected issues
    """
    issues = []
    
    issues.extend(detect_objective_statement(cv_text))
    issues.extend(detect_references_section(cv_text))
    issues.extend(detect_outdated_skills(cv_text))
    issues.extend(detect_hobbies_irrelevant(cv_text))
    issues.extend(detect_unprofessional_language(cv_text))
    issues.extend(detect_negative_language(cv_text))
    issues.extend(detect_employment_gap(cv_text))
    
    return issues


def detect_objective_statement(cv_text: str) -> List[Dict[str, Any]]:
    """
    Detect outdated objective statement (should use Summary instead).
    """
    issues = []
    
    patterns = [
        r'\b[Oo]bjective\s*:',
        r'\b[Cc]areer\s+[Oo]bjective\b',
        r'\b[Jj]ob\s+[Oo]bjective\b',
        r'\b[Ss]eeking\s+(a\s+)?(position|role|opportunity)\b',
        r'\b[Ll]ooking\s+for\s+(a\s+)?(position|role|opportunity)\b',
        r'\b[Tt]o\s+obtain\s+(a\s+)?(position|role)\b',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, cv_text)
        if match:
            issues.append({
                "issue_type": "STANDARDS_OBJECTIVE_STATEMENT",
                "location": f"Found at position {match.start()}",
                "description": "CV contains outdated objective statement. Modern CVs use Professional Summary instead.",
                "current": match.group(),
                "suggestion": "Replace with a Professional Summary highlighting your value proposition"
            })
            break
    
    return issues


def detect_references_section(cv_text: str) -> List[Dict[str, Any]]:
    """
    Detect unnecessary references section.
    """
    issues = []
    
    patterns = [
        r'\b[Rr]eferences\s*:?\s*(available\s+)?(upon|on)\s+request\b',
        r'\b[Rr]eferences\s+[Aa]vailable\b',
        r'\b[Rr]eferences\s*:\s*\n',
        r'\b[Pp]rofessional\s+[Rr]eferences\b',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, cv_text)
        if match:
            issues.append({
                "issue_type": "STANDARDS_REFERENCES_SECTION",
                "location": "References section",
                "description": "References section is unnecessary. Employers assume references are available.",
                "current": match.group(),
                "suggestion": "Remove references section to save space for achievements"
            })
            break
    
    return issues


def detect_outdated_skills(cv_text: str) -> List[Dict[str, Any]]:
    """
    Detect obsolete technologies/skills that hurt credibility.
    """
    issues = []
    
    outdated_skills = {
        'COBOL': 'programming language',
        'FORTRAN': 'programming language',
        'Pascal': 'programming language',
        'Visual Basic 6': 'programming language',
        'VB6': 'programming language',
        'Flash': 'web technology',
        'ActionScript': 'web technology',
        'Silverlight': 'web technology',
        'FrontPage': 'web tool',
        'Dreamweaver': 'web tool',
        'ColdFusion': 'web technology',
        'Windows XP': 'operating system',
        'Windows Vista': 'operating system',
        'Windows 7': 'operating system',
        'Windows 95': 'operating system',
        'Windows 98': 'operating system',
        'MS-DOS': 'operating system',
        'DOS': 'operating system',
        'Lotus Notes': 'software',
        'Lotus 1-2-3': 'software',
        'WordPerfect': 'software',
        'FoxPro': 'database',
        'dBase': 'database',
        'Clipper': 'database',
        'Fax machine': 'equipment',
        'Telex': 'equipment',
        'Typing speed': 'skill',
    }
    
    found_outdated = []
    cv_lower = cv_text.lower()
    
    for skill, category in outdated_skills.items():
        if skill.lower() in cv_lower:
            found_outdated.append(f"{skill} ({category})")
    
    if found_outdated:
        issues.append({
            "issue_type": "STANDARDS_OUTDATED_SKILLS",
            "location": "Skills/Technologies section",
            "description": f"CV lists outdated technologies: {', '.join(found_outdated[:5])}",
            "current": ', '.join(found_outdated),
            "suggestion": "Remove outdated skills unless specifically required for the role"
        })
    
    return issues


def detect_hobbies_irrelevant(cv_text: str) -> List[Dict[str, Any]]:
    """
    Detect generic hobbies that don't add value.
    """
    issues = []
    
    hobbies_section = re.search(
        r'\b(Hobbies|Interests|Personal\s+Interests|Activities)\s*:?\s*\n(.*?)(?=\n[A-Z]|\Z)',
        cv_text,
        re.IGNORECASE | re.DOTALL
    )
    
    if hobbies_section:
        section_text = hobbies_section.group(2).lower()
        
        generic_hobbies = [
            'reading', 'traveling', 'music', 'movies', 'cooking',
            'sports', 'fitness', 'gym', 'yoga', 'running',
            'photography', 'gardening', 'hiking', 'camping',
            'socializing', 'spending time with family', 'friends'
        ]
        
        found_generic = [h for h in generic_hobbies if h in section_text]
        
        if len(found_generic) >= 2:
            issues.append({
                "issue_type": "STANDARDS_HOBBIES_IRRELEVANT",
                "location": "Hobbies/Interests section",
                "description": "Generic hobbies don't differentiate you. Include only if relevant to role.",
                "current": ', '.join(found_generic[:5]),
                "suggestion": "Remove generic hobbies or replace with role-relevant activities"
            })
    
    return issues


def detect_unprofessional_language(cv_text: str) -> List[Dict[str, Any]]:
    """
    Detect informal or unprofessional language.
    """
    issues = []
    
    patterns = {
        r'\b(gonna|wanna|gotta|kinda|sorta)\b': 'slang contraction',
        r'\b(stuff|things|whatever)\b': 'vague informal word',
        r'!{2,}': 'multiple exclamation marks',
        r'\.{3,}': 'excessive ellipsis',
        r'\b(awesome|amazing|incredible|insane)\b': 'hyperbolic word',
        r'\b(rockstar|ninja|guru|wizard|unicorn)\b': 'buzzword title',
        r'\b(lol|omg|btw|idk|tbh|imho)\b': 'internet slang',
        r'[😀😃😄😁😆🤣😂🙂🙃😉😊😇]': 'emoji',
        r'\b(etc\.?\s*){2,}': 'repeated etc',
    }
    
    found_issues = []
    
    for pattern, issue_type in patterns.items():
        matches = re.findall(pattern, cv_text, re.IGNORECASE)
        if matches:
            match_text = matches[0] if isinstance(matches[0], str) else str(matches[0])
            found_issues.append(f"{issue_type}: {match_text}")
    
    if found_issues:
        issues.append({
            "issue_type": "STANDARDS_UNPROFESSIONAL_LANGUAGE",
            "location": "Throughout CV",
            "description": f"Unprofessional language detected: {', '.join(found_issues[:3])}",
            "current": ', '.join(found_issues),
            "suggestion": "Use formal, professional language throughout your CV"
        })
    
    return issues


def detect_negative_language(cv_text: str) -> List[Dict[str, Any]]:
    """
    Detect negative language or criticism of past employers.
    """
    issues = []
    
    negative_patterns = [
        r'\b(hated|hate|terrible|awful|worst|horrible)\b',
        r'\b(bad\s+management|poor\s+leadership|toxic)\b',
        r'\b(fired|terminated|let\s+go|laid\s+off)\b',
        r'\b(conflict|disagreement|dispute)\s+with\b',
        r'\b(unfair|discrimination|harassment)\b',
        r'\b(failure|failed|unsuccessful)\b',
        r'\b(boring|tedious|mundane)\b',
        r'\b(unfortunately|regrettably)\b',
        r'\b(forced\s+to|had\s+to\s+leave)\b',
    ]
    
    found_negative = []
    
    for pattern in negative_patterns:
        match = re.search(pattern, cv_text, re.IGNORECASE)
        if match:
            found_negative.append(match.group())
    
    if found_negative:
        issues.append({
            "issue_type": "STANDARDS_NEGATIVE_LANGUAGE",
            "location": "Throughout CV",
            "description": "Negative language can hurt your candidacy",
            "current": ', '.join(found_negative[:3]),
            "suggestion": "Reframe negatively using positive language focusing on growth and learning"
        })
    
    return issues


def detect_employment_gap(cv_text: str) -> List[Dict[str, Any]]:
    """
    Detect employment gaps > 6 months.
    """
    from datetime import datetime
    
    issues = []
    
    month_map = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    dates_found = []
    
    present_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(\d{4})\s*[-–—to]+\s*[Pp]resent'
    present_matches = re.findall(present_pattern, cv_text, re.IGNORECASE)
    for match in present_matches:
        try:
            start_month = month_map.get(match[0][:3].lower(), 1)
            start_year = int(match[1])
            dates_found.append((start_year, start_month, current_year, current_month))
        except (ValueError, IndexError):
            continue
    
    full_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(\d{4})\s*[-–—to]+\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(\d{4})'
    full_matches = re.findall(full_pattern, cv_text, re.IGNORECASE)
    for match in full_matches:
        try:
            start_month = month_map.get(match[0][:3].lower(), 1)
            start_year = int(match[1])
            end_month = month_map.get(match[2][:3].lower(), 12)
            end_year = int(match[3])
            dates_found.append((start_year, start_month, end_year, end_month))
        except (ValueError, IndexError):
            continue
    
    year_pattern = r'(\d{4})\s*[-–—to]+\s*(\d{4})'
    year_matches = re.findall(year_pattern, cv_text)
    for match in year_matches:
        try:
            dates_found.append((int(match[0]), 1, int(match[1]), 12))
        except (ValueError, IndexError):
            continue
    
    dates_found.sort(key=lambda x: (x[2], x[3]), reverse=True)
    
    gaps_found = []
    for i in range(len(dates_found) - 1):
        current_job = dates_found[i]
        previous_job = dates_found[i + 1]
        
        current_start = current_job[0] * 12 + current_job[1]
        previous_end = previous_job[2] * 12 + previous_job[3]
        
        gap_months = current_start - previous_end
        
        if gap_months > 6:
            gaps_found.append(f"{gap_months} months gap around {previous_job[2]}-{current_job[0]}")
    
    if gaps_found:
        issues.append({
            "issue_type": "CAREER_EMPLOYMENT_GAP",
            "location": "Experience section",
            "description": f"Employment gap(s) detected: {gaps_found[0]}",
            "current": ', '.join(gaps_found[:2]),
            "suggestion": "Address gaps by noting activities (freelance, education, caregiving, etc.)"
        })
    
    return issues
