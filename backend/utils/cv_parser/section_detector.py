"""
Section Detector Module
Identifies CV sections using keyword matching
"""

import re
from typing import Dict, List, Tuple, Optional, Any

SECTION_HEADERS = {
    'summary': [
        'summary', 'professional summary', 'executive summary',
        'objective', 'career objective', 'profile', 'about', 'about me',
        'personal statement', 'overview', 'introduction'
    ],
    'experience': [
        'experience', 'work experience', 'professional experience',
        'employment history', 'employment', 'work history', 
        'career history', 'professional background', 'positions held'
    ],
    'education': [
        'education', 'academic background', 'qualifications',
        'education and training', 'academic qualifications',
        'educational background', 'academic history', 'degrees',
        'educational qualifications', 'academic credentials'
    ],
    'skills': [
        'skills', 'technical skills', 'core competencies',
        'key skills', 'professional skills', 'expertise',
        'competencies', 'areas of expertise', 'technical competencies',
        'skills and abilities', 'core skills', 'key competencies'
    ],
    'certifications': [
        'certifications', 'certificates', 'licenses',
        'professional certifications', 'credentials',
        'accreditations', 'professional licenses',
        'certifications and licenses', 'professional credentials'
    ],
    'projects': [
        'projects', 'key projects', 'selected projects',
        'project experience', 'notable projects', 'personal projects',
        'professional projects', 'project highlights'
    ],
    'achievements': [
        'achievements', 'accomplishments', 'awards', 'honors',
        'recognition', 'key achievements', 'awards and honors',
        'achievements and awards', 'notable achievements'
    ],
    'publications': [
        'publications', 'papers', 'research', 'published works',
        'academic publications', 'articles', 'research papers'
    ],
    'languages': [
        'languages', 'language skills', 'language proficiency',
        'foreign languages', 'linguistic skills'
    ],
    'interests': [
        'interests', 'hobbies', 'personal interests',
        'hobbies and interests', 'extracurricular activities'
    ],
    'volunteer': [
        'volunteer', 'volunteer experience', 'volunteering',
        'community service', 'volunteer work', 'civic activities'
    ],
    'references': [
        'references', 'professional references', 'referees'
    ]
}

HEBREW_SECTION_HEADERS = {
    'summary': ['תקציר', 'אודות', 'אודותיי', 'פרופיל'],
    'experience': ['ניסיון תעסוקתי', 'ניסיון מקצועי', 'ניסיון', 'היסטוריה תעסוקתית'],
    'education': ['השכלה', 'לימודים', 'רקע אקדמי'],
    'skills': ['כישורים', 'מיומנויות', 'יכולות', 'מומחיות'],
    'certifications': ['הסמכות', 'תעודות', 'רישיונות'],
    'projects': ['פרויקטים', 'פרוייקטים'],
    'languages': ['שפות'],
    'military': ['שירות צבאי', 'צבא', 'שירות לאומי']
}


def detect_sections(text: str) -> Dict[str, Any]:
    """
    Detect sections in CV text.
    
    Args:
        text: Raw CV text
        
    Returns:
        Dictionary with detected sections and their content
    """
    lines = text.split('\n')
    
    section_positions = []
    
    for i, line in enumerate(lines):
        line_clean = line.strip().lower()
        line_clean_no_punct = re.sub(r'[^\w\s]', '', line_clean)
        
        for section_name, keywords in SECTION_HEADERS.items():
            for keyword in keywords:
                if line_clean_no_punct == keyword or line_clean_no_punct.startswith(keyword + ' '):
                    section_positions.append((i, section_name, line.strip()))
                    break
            else:
                continue
            break
        
        for section_name, keywords in HEBREW_SECTION_HEADERS.items():
            for keyword in keywords:
                if keyword in line_clean:
                    section_positions.append((i, section_name, line.strip()))
                    break
    
    sections_found = {}
    section_content = {}
    
    for idx, (line_idx, section_name, header_text) in enumerate(section_positions):
        if idx + 1 < len(section_positions):
            end_idx = section_positions[idx + 1][0]
        else:
            end_idx = len(lines)
        
        content_lines = lines[line_idx + 1:end_idx]
        content = '\n'.join(content_lines).strip()
        
        sections_found[section_name] = True
        section_content[section_name] = {
            'header': header_text,
            'content': content[:2000],
            'line_count': len([l for l in content_lines if l.strip()]),
            'start_line': line_idx
        }
    
    all_sections = list(SECTION_HEADERS.keys())
    missing_sections = [s for s in all_sections if s not in sections_found]
    
    return {
        'sections_found': list(sections_found.keys()),
        'sections_missing': missing_sections,
        'section_count': len(sections_found),
        'content': section_content,
        'has_summary': 'summary' in sections_found,
        'has_experience': 'experience' in sections_found,
        'has_education': 'education' in sections_found,
        'has_skills': 'skills' in sections_found
    }


def get_section_content(text: str, section_name: str) -> Optional[str]:
    """
    Get content of a specific section.
    
    Args:
        text: Raw CV text
        section_name: Name of section to extract
        
    Returns:
        Section content or None if not found
    """
    sections = detect_sections(text)
    if section_name in sections['content']:
        return sections['content'][section_name]['content']
    return None
