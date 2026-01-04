"""
Skills Extractor Module
Extracts skills from CV using predefined skills database
"""

import os
import re
from typing import List, Set, Dict, Optional, Any

DEFAULT_SKILLS = {
    'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'sql', 
    'typescript', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r',
    'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
    'django', 'flask', 'spring', 'asp.net', 'jquery', 'bootstrap',
    'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
    'oracle', 'sql server', 'sqlite', 'dynamodb', 'cassandra',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
    'terraform', 'ansible', 'git', 'github', 'gitlab', 'ci/cd',
    'machine learning', 'deep learning', 'tensorflow', 'pytorch',
    'pandas', 'numpy', 'scikit-learn', 'keras', 'nlp', 'computer vision',
    'jira', 'confluence', 'slack', 'trello', 'figma', 'sketch',
    'photoshop', 'excel', 'powerpoint', 'word', 'salesforce',
    'agile', 'scrum', 'kanban', 'waterfall', 'devops',
    'leadership', 'communication', 'teamwork', 'problem solving',
    'project management', 'time management', 'analytical skills',
    'presentation', 'negotiation', 'customer service'
}


def load_skills_database(file_path: Optional[str] = None) -> Set[str]:
    """
    Load skills database from CSV file or use default.
    
    Args:
        file_path: Path to custom skills CSV file
        
    Returns:
        Set of skills (lowercase)
    """
    skills = set()
    
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                raw_skills = content.replace('\n', ',').split(',')
                skills = {s.strip().lower() for s in raw_skills if s.strip()}
        except Exception as e:
            print(f"Error loading skills file: {e}")
    
    if not skills:
        default_path = os.path.join(os.path.dirname(__file__), 'data', 'skills.csv')
        if os.path.exists(default_path):
            try:
                with open(default_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    raw_skills = content.replace('\n', ',').split(',')
                    skills = {s.strip().lower() for s in raw_skills if s.strip()}
            except Exception as e:
                print(f"Error loading default skills file: {e}")
    
    if not skills:
        skills = DEFAULT_SKILLS.copy()
    
    return skills


def extract_skills(text: str, skills_db: Optional[Set[str]] = None) -> Dict[str, Any]:
    """
    Extract skills from CV text.
    
    Args:
        text: Raw CV text
        skills_db: Set of known skills (lowercase)
        
    Returns:
        Dictionary with found skills and metadata
    """
    if skills_db is None:
        skills_db = load_skills_database()
    
    text_lower = text.lower()
    found_skills = []
    skill_positions = {}
    
    sorted_skills = sorted(skills_db, key=len, reverse=True)
    
    for skill in sorted_skills:
        skill_pattern = r'\b' + re.escape(skill) + r'\b'
        
        matches = list(re.finditer(skill_pattern, text_lower))
        if matches:
            if skill not in found_skills:
                is_substring = False
                for found in found_skills:
                    if skill in found:
                        is_substring = True
                        break
                
                if not is_substring:
                    found_skills.append(skill)
                    skill_positions[skill] = matches[0].start()
    
    categories = categorize_skills(found_skills)
    
    return {
        'skills_found': found_skills,
        'skill_count': len(found_skills),
        'categories': categories,
        'top_skills': found_skills[:20],
        'has_programming': bool(categories.get('programming', [])),
        'has_cloud': bool(categories.get('cloud', [])),
        'has_data': bool(categories.get('data_science', []))
    }


def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """Categorize skills into groups."""
    
    categories = {
        'programming': [],
        'web': [],
        'database': [],
        'cloud': [],
        'data_science': [],
        'tools': [],
        'soft_skills': [],
        'other': []
    }
    
    programming_keywords = {'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 
                           'php', 'typescript', 'go', 'rust', 'swift', 'kotlin',
                           'scala', 'r', 'perl', 'matlab', 'sql'}
    
    web_keywords = {'html', 'css', 'react', 'angular', 'vue', 'node', 'express',
                   'django', 'flask', 'spring', 'asp', 'jquery', 'bootstrap',
                   'webpack', 'rest', 'api', 'graphql'}
    
    database_keywords = {'mysql', 'postgresql', 'mongodb', 'redis', 'oracle',
                        'sql server', 'sqlite', 'dynamodb', 'cassandra', 'nosql',
                        'elasticsearch', 'database'}
    
    cloud_keywords = {'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
                     'terraform', 'ansible', 'devops', 'ci/cd', 'cloud'}
    
    data_keywords = {'machine learning', 'deep learning', 'tensorflow', 'pytorch',
                    'pandas', 'numpy', 'scikit', 'keras', 'nlp', 'data science',
                    'analytics', 'big data', 'spark', 'hadoop'}
    
    soft_keywords = {'leadership', 'communication', 'teamwork', 'management',
                    'problem solving', 'analytical', 'presentation', 'negotiation'}
    
    for skill in skills:
        skill_lower = skill.lower()
        
        if any(kw in skill_lower for kw in programming_keywords):
            categories['programming'].append(skill)
        elif any(kw in skill_lower for kw in web_keywords):
            categories['web'].append(skill)
        elif any(kw in skill_lower for kw in database_keywords):
            categories['database'].append(skill)
        elif any(kw in skill_lower for kw in cloud_keywords):
            categories['cloud'].append(skill)
        elif any(kw in skill_lower for kw in data_keywords):
            categories['data_science'].append(skill)
        elif any(kw in skill_lower for kw in soft_keywords):
            categories['soft_skills'].append(skill)
        else:
            categories['other'].append(skill)
    
    return {k: v for k, v in categories.items() if v}
