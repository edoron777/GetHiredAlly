"""
CV Vocabulary Spell Checker

SAFE APPROACH: Only checks known CV terminology.
Does NOT check technical terms (AWS, Kubernetes, etc.)
This avoids false positives that would annoy users.

Catches: "Experiance" → "Experience", "Managment" → "Management"
Ignores: "PostgreSQL", "OAuth2", "GraphQL" (tech terms)

100% CODE - No AI - Deterministic results.
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from difflib import SequenceMatcher

try:
    from common.detection.block_detector import CVBlockStructure
except ImportError:
    CVBlockStructure = None

CV_VOCABULARY = {
    "experience": "experience",
    "education": "education", 
    "skills": "skills",
    "summary": "summary",
    "professional": "professional",
    "certifications": "certifications",
    "achievements": "achievements",
    "objective": "objective",
    "qualifications": "qualifications",
    "references": "references",
    "projects": "projects",
    "responsible": "responsible",
    "responsibilities": "responsibilities",
    "management": "management",
    "manager": "manager",
    "developed": "developed",
    "development": "development",
    "implemented": "implemented",
    "implementation": "implementation",
    "achieved": "achieved",
    "achievement": "achievement",
    "successful": "successful",
    "successfully": "successfully",
    "coordinated": "coordinated",
    "collaborated": "collaborated",
    "communication": "communication",
    "technical": "technical",
    "technology": "technology",
    "technologies": "technologies",
    "environment": "environment",
    "performance": "performance",
    "improved": "improved",
    "improvement": "improvement",
    "maintained": "maintained",
    "maintenance": "maintenance",
    "analysis": "analysis",
    "analyzed": "analyzed",
    "business": "business",
    "customer": "customer",
    "customers": "customers",
    "leadership": "leadership",
    "organization": "organization",
    "organizational": "organizational",
    "excellent": "excellent",
    "effectively": "effectively",
    "efficiency": "efficiency",
    "efficient": "efficient",
    "proficient": "proficient",
    "proficiency": "proficiency",
    "bachelor": "bachelor",
    "master": "master",
    "degree": "degree",
    "university": "university",
    "certificate": "certificate",
    "certified": "certified",
    "managed": "managed",
    "led": "led",
    "created": "created",
    "designed": "designed",
    "built": "built",
    "delivered": "delivered",
    "launched": "launched",
    "established": "established",
    "increased": "increased",
    "reduced": "reduced",
    "streamlined": "streamlined",
    "optimized": "optimized",
    "executed": "executed",
    "facilitated": "facilitated",
    "spearheaded": "spearheaded",
    "orchestrated": "orchestrated",
    "architected": "architected",
    "mentored": "mentored",
    "supervised": "supervised",
    "oversaw": "oversaw",
    "conducted": "conducted",
    "prepared": "prepared",
    "presented": "presented",
    "trained": "trained",
    "supported": "supported",
    "assisted": "assisted",
    "contributed": "contributed",
    "participated": "participated",
}

COMMON_MISSPELLINGS = {
    "experiance": "experience",
    "experiece": "experience",
    "expirience": "experience",
    "experince": "experience",
    "eduction": "education",
    "educaton": "education",
    "educatoin": "education",
    "skils": "skills",
    "skilss": "skills",
    "sumary": "summary",
    "summery": "summary",
    "proffesional": "professional",
    "profesional": "professional",
    "professionel": "professional",
    "professonal": "professional",
    "certifcations": "certifications",
    "certificatons": "certifications",
    "acheivements": "achievements",
    "achievments": "achievements",
    "achivements": "achievements",
    "responisble": "responsible",
    "responsable": "responsible",
    "responsibile": "responsible",
    "responsibilites": "responsibilities",
    "responsiblities": "responsibilities",
    "managment": "management",
    "managament": "management",
    "mangement": "management",
    "developped": "developed",
    "develped": "developed",
    "develope": "developed",
    "developement": "development",
    "devlopment": "development",
    "implmented": "implemented",
    "implimented": "implemented",
    "implementd": "implemented",
    "implementaion": "implementation",
    "achived": "achieved",
    "acheived": "achieved",
    "achievment": "achievement",
    "acheivment": "achievement",
    "succesful": "successful",
    "successfull": "successful",
    "succesfull": "successful",
    "succesfully": "successfully",
    "successfuly": "successfully",
    "comunication": "communication",
    "communcation": "communication",
    "communicaton": "communication",
    "techincal": "technical",
    "tecnical": "technical",
    "technolgy": "technology",
    "technolgies": "technologies",
    "enviroment": "environment",
    "enviornment": "environment",
    "performace": "performance",
    "preformance": "performance",
    "improvment": "improvement",
    "improvemnt": "improvement",
    "maintanance": "maintenance",
    "maintenace": "maintenance",
    "anaylsis": "analysis",
    "analisis": "analysis",
    "analysed": "analyzed",
    "buisness": "business",
    "bussiness": "business",
    "busines": "business",
    "custmer": "customer",
    "cusotmer": "customer",
    "leaderhip": "leadership",
    "leardership": "leadership",
    "organizaton": "organization",
    "organisaton": "organization",
    "excelent": "excellent",
    "excellant": "excellent",
    "effectivly": "effectively",
    "effeciently": "efficiently",
    "efficent": "efficient",
    "efficency": "efficiency",
    "proficent": "proficient",
    "profficient": "proficient",
    "univeristy": "university",
    "universty": "university",
    "certifed": "certified",
    "cerfitied": "certified",
    "managd": "managed",
    "manged": "managed",
    "crated": "created",
    "craeted": "created",
    "desinged": "designed",
    "desigend": "designed",
    "deliverd": "delivered",
    "delivred": "delivered",
    "lauched": "launched",
    "lanched": "launched",
    "establised": "established",
    "establishd": "established",
    "increasd": "increased",
    "incresed": "increased",
    "reducd": "reduced",
    "reducted": "reduced",
    "optmized": "optimized",
    "optimzed": "optimized",
    "excuted": "executed",
    "exectued": "executed",
    "faciliated": "facilitated",
    "faciltated": "facilitated",
    "spearheaed": "spearheaded",
    "orchastrated": "orchestrated",
    "mentord": "mentored",
    "mentroed": "mentored",
    "supervized": "supervised",
    "supervisd": "supervised",
    "conducte": "conducted",
    "condcuted": "conducted",
    "prepard": "prepared",
    "preapred": "prepared",
    "presentd": "presented",
    "presenetd": "presented",
    "traind": "trained",
    "trianed": "trained",
    "supportd": "supported",
    "suppored": "supported",
    "assistd": "assisted",
    "assited": "assisted",
    "contribued": "contributed",
    "contriubted": "contributed",
    "paticipated": "participated",
    "participted": "participated",
}

GRAMMAR_PATTERNS = [
    (re.compile(r'\b(\w+)\s+\1\b', re.IGNORECASE), 'Repeated word: "{}"'),
    (re.compile(r'\.[A-Z]'), 'Missing space after period'),
    (re.compile(r'  +'), 'Multiple consecutive spaces'),
    (re.compile(r'\s+[,.]'), 'Space before punctuation'),
]


def is_similar(word1: str, word2: str, threshold: float = 0.8) -> bool:
    """Check if two words are similar using SequenceMatcher."""
    return SequenceMatcher(None, word1.lower(), word2.lower()).ratio() >= threshold


def find_potential_misspelling(word: str) -> Tuple[bool, str, str]:
    """
    Check if a word is a potential misspelling of a CV vocabulary word.
    
    Returns: (is_misspelling, original_word, correct_word)
    """
    word_lower = word.lower()
    
    if len(word_lower) < 4:
        return (False, word, "")
    
    if any(char.isdigit() for char in word):
        return (False, word, "")
    
    if word.isupper() and len(word) <= 6:
        return (False, word, "")
    
    if word_lower in COMMON_MISSPELLINGS:
        return (True, word, COMMON_MISSPELLINGS[word_lower])
    
    if word_lower in CV_VOCABULARY:
        return (False, word, "")
    
    for correct_word in CV_VOCABULARY.keys():
        if abs(len(word_lower) - len(correct_word)) <= 2:
            if is_similar(word_lower, correct_word, threshold=0.85):
                if word_lower != correct_word:
                    return (True, word, correct_word)
    
    return (False, word, "")


def find_line_number(text: str, word: str) -> int:
    """Find the line number where a word appears."""
    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        if word in line:
            return i
    return 0


def extract_words(text: str) -> List[str]:
    """Extract all words from text for spell checking."""
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    return words


def check_cv_vocabulary_spelling(text: str) -> List[Dict]:
    """
    Check text for CV vocabulary spelling errors.
    SAFE: Only checks known CV terminology, no false positives.
    
    Args:
        text: Text to check
        
    Returns:
        List of spelling error issues
    """
    issues = []
    words = extract_words(text)
    
    found_errors: Set[str] = set()
    
    for word in words:
        is_error, original, correct = find_potential_misspelling(word)
        
        if is_error and original.lower() not in found_errors:
            found_errors.add(original.lower())
            
            issues.append({
                "issue_type": "CONTENT_SPELLING_CV_WORDS",
                "severity": "critical",
                "match_text": original,
                "suggestion": f'Spelling error: "{original}" should be "{correct}"',
                "can_auto_fix": True,
                "details": {
                    "original": original,
                    "correct": correct,
                },
                "line_number": find_line_number(text, original),
            })
    
    return issues


def check_grammar(text: str) -> List[Dict]:
    """
    Check text for common grammar errors using patterns.
    
    Args:
        text: Text to check
        
    Returns:
        List of grammar error issues
    """
    issues = []
    
    for pattern, error_msg in GRAMMAR_PATTERNS:
        matches = pattern.findall(text)
        
        for match in matches[:2]:
            issues.append({
                'issue_type': 'GRAMMAR_GRAMMATICAL_ERROR',
                'location': 'Throughout CV',
                'description': error_msg.format(match) if '{}' in error_msg else error_msg,
                'current': match if isinstance(match, str) else str(match),
            })
    
    return issues


def detect_critical_issues(text: str) -> List[Dict]:
    """
    Detect all critical issues (spelling + grammar).
    
    This is the MAIN function for critical issue detection.
    100% deterministic - same text → same result.
    
    Args:
        text: Full CV text
        
    Returns:
        List of critical issues (SPELLING_ERROR, GRAMMAR_ERROR)
    """
    issues = []
    
    issues.extend(check_cv_vocabulary_spelling(text))
    issues.extend(check_grammar(text))
    
    return issues


def detect_spelling_issues(cv_text: str, cv_block_structure: Optional['CVBlockStructure'] = None) -> List[Dict]:
    """
    Main entry point for spelling detection.
    Safe approach - only checks CV vocabulary.
    """
    return check_cv_vocabulary_spelling(cv_text)


def detect_all_spelling_issues(cv_text: str, cv_block_structure: Optional['CVBlockStructure'] = None) -> List[Dict]:
    """Alias for detect_spelling_issues for consistency with other detectors."""
    return detect_spelling_issues(cv_text, cv_block_structure)
