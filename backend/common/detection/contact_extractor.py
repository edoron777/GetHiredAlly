"""
Contact Information Extractor

Extracts contact details using REGEX patterns.
100% CODE - No AI - Deterministic results.
"""

import re
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class ContactInfo:
    """Structured contact information from CV."""
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    
    has_email: bool = False
    has_phone: bool = False
    has_linkedin: bool = False
    email_valid: bool = True
    phone_valid: bool = True


EMAIL_PATTERN = re.compile(
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    re.IGNORECASE
)

PHONE_PATTERNS = [
    re.compile(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'),
    re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
    re.compile(r'\b\d{10,12}\b'),
]

LINKEDIN_PATTERN = re.compile(
    r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+/?',
    re.IGNORECASE
)

GITHUB_PATTERN = re.compile(
    r'(?:https?://)?(?:www\.)?github\.com/[\w-]+/?',
    re.IGNORECASE
)

WEBSITE_PATTERN = re.compile(
    r'(?:https?://)?(?:www\.)?[\w-]+\.[\w.-]+(?:/[\w.-]*)*',
    re.IGNORECASE
)

LOCATION_PATTERNS = [
    re.compile(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b'),
    re.compile(r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b'),
    re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+,\s*[A-Z]{2}\b'),
]

TECH_KEYWORDS = [
    'python', 'java', 'javascript', 'developer', 'engineer', 'software',
    'react', 'node', 'backend', 'frontend', 'fullstack', 'full-stack',
    'devops', 'data scientist', 'machine learning', 'ml', 'ai',
    'programming', 'coding', 'typescript', 'golang', 'rust', 'c++', 'c#',
]

UNPROFESSIONAL_EMAIL_WORDS = [
    'hot', 'sexy', 'cool', 'party', 'babe', 'cute', 'princess', 'angel',
    'devil', 'crazy', 'killer', 'gamer', 'ninja', 'warrior', 'dragon',
    'xxx', 'love', 'sweetie', 'honey', 'baby', 'dude', 'stud', 'punk',
]

PHOTO_INDICATORS = [
    re.compile(r'\[photo\]', re.IGNORECASE),
    re.compile(r'\[image\]', re.IGNORECASE),
    re.compile(r'\[picture\]', re.IGNORECASE),
    re.compile(r'<img', re.IGNORECASE),
    re.compile(r'photo\s*:', re.IGNORECASE),
]

# Separators used in contact lines (pipe, bullet, etc.)
# Note: '/' removed because it appears in URLs (linkedin.com/in/...) causing false positives
CONTACT_SEPARATORS = ['|', '•', '·', '–', '—']

INVALID_EMAIL_PATTERNS = [
    re.compile(r'^[^@]+$'),
    re.compile(r'@[^.]+$'),
    re.compile(r'\.{2,}'),
    re.compile(r'^\.'),
    re.compile(r'\.$'),
]


def extract_email(text: str) -> Optional[str]:
    """Extract first email address from text."""
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_all_emails(text: str) -> List[str]:
    """Extract all email addresses from text."""
    return EMAIL_PATTERN.findall(text)


def validate_email(email: str) -> bool:
    """Check if email format is valid."""
    if not email:
        return False
    
    if '@' not in email:
        return False
    
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    local, domain = parts
    
    if not local or len(local) > 64:
        return False
    
    if not domain or '.' not in domain:
        return False
    
    for pattern in INVALID_EMAIL_PATTERNS:
        if pattern.search(email):
            return False
    
    return True


def extract_phone(text: str) -> Optional[str]:
    """Extract first phone number from text."""
    for pattern in PHONE_PATTERNS:
        match = pattern.search(text)
        if match:
            phone = match.group(0)
            digits = re.sub(r'[^\d+\-() ]', '', phone)
            if len(re.sub(r'\D', '', digits)) >= 7:
                return digits
    return None


def validate_phone(phone: str) -> bool:
    """Check if phone has enough digits."""
    if not phone:
        return False
    
    digits = re.sub(r'\D', '', phone)
    return 7 <= len(digits) <= 15


def extract_linkedin(text: str) -> Optional[str]:
    """Extract LinkedIn URL from text."""
    match = LINKEDIN_PATTERN.search(text)
    return match.group(0) if match else None


def extract_github(text: str) -> Optional[str]:
    """Extract GitHub URL from text."""
    match = GITHUB_PATTERN.search(text)
    return match.group(0) if match else None


def extract_location(text: str) -> Optional[str]:
    """Extract location (City, State) from first 500 chars of text."""
    contact_area = text[:500]
    for pattern in LOCATION_PATTERNS:
        match = pattern.search(contact_area)
        if match:
            return match.group(0)
    return None


def is_tech_cv(text: str) -> bool:
    """Check if CV is for a tech role."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in TECH_KEYWORDS)


def check_unprofessional_email(email: str) -> Optional[str]:
    """Check if email contains unprofessional patterns."""
    if not email:
        return None
    
    email_lower = email.lower()
    local_part = email_lower.split('@')[0] if '@' in email_lower else email_lower
    
    for word in UNPROFESSIONAL_EMAIL_WORDS:
        if word in local_part:
            return word
    
    numbers_match = re.search(r'\d{3,}', local_part)
    if numbers_match:
        num = numbers_match.group(0)
        if len(num) != 4 or not (1950 <= int(num) <= 2010):
            return f"excessive numbers ({num})"
    
    return None


def check_photo_included(text: str) -> bool:
    """Check for photo/image indicators in CV."""
    for pattern in PHOTO_INDICATORS:
        if pattern.search(text):
            return True
    return False


def check_inconsistent_separators(text: str) -> Optional[List[str]]:
    """Check for mixed separators in contact section."""
    contact_area = text[:500]
    found_separators = []
    
    for sep in CONTACT_SEPARATORS:
        if sep in contact_area:
            found_separators.append(sep)
    
    if len(found_separators) > 1:
        return found_separators
    return None


def detect_linkedin_no_url(text: str) -> List[Dict]:
    """
    Detect when LinkedIn is mentioned but no actual URL is provided.
    
    SCENARIO:
    - "LinkedIn" or "linkedin" text appears
    - BUT no linkedin.com/in/ URL is found
    - This is different from MISSING LinkedIn (no mention at all)
    """
    issues = []
    
    text_lower = text.lower()
    
    linkedin_mentioned = 'linkedin' in text_lower
    
    if not linkedin_mentioned:
        return issues
    
    linkedin_url_patterns = [
        r'linkedin\.com/in/[\w\-]+',
        r'linkedin\.com/pub/[\w\-]+',
        r'www\.linkedin\.com/in/[\w\-]+',
        r'https?://(?:www\.)?linkedin\.com/in/[\w\-]+',
    ]
    
    has_url = False
    for pattern in linkedin_url_patterns:
        if re.search(pattern, text_lower):
            has_url = True
            break
    
    if not has_url:
        linkedin_match = re.search(r'\blinkedin\b', text, re.IGNORECASE)
        match_text = linkedin_match.group() if linkedin_match else 'LinkedIn'
        
        issues.append({
            'issue_type': 'CONTACT_LINKEDIN_NO_URL',
            'match_text': match_text,
            'suggestion': 'You mention LinkedIn but did not include your profile URL. Add your full LinkedIn URL (e.g., linkedin.com/in/yourname) so recruiters can easily find you.',
            'can_auto_fix': False,
            'severity': 'important'
        })
    
    return issues


def extract_contact_info(text: str) -> ContactInfo:
    """
    Extract all contact information from CV text.
    
    This is the MAIN function for contact extraction.
    100% deterministic - same text → same result.
    
    Args:
        text: Full CV text
        
    Returns:
        ContactInfo dataclass with all extracted info and validation flags
    """
    info = ContactInfo()
    
    info.email = extract_email(text)
    info.has_email = info.email is not None
    info.email_valid = validate_email(info.email) if info.email else True
    
    info.phone = extract_phone(text)
    info.has_phone = info.phone is not None
    info.phone_valid = validate_phone(info.phone) if info.phone else True
    
    info.linkedin = extract_linkedin(text)
    info.has_linkedin = info.linkedin is not None
    
    info.github = extract_github(text)
    
    return info


def get_contact_issues(contact: ContactInfo, full_text: str = "") -> List[Dict]:
    """
    Generate issues based on contact info extraction.
    
    Args:
        contact: ContactInfo object with extracted data
        full_text: Full CV text for additional checks
    
    Returns list of issue dictionaries with issue_type.
    Each issue includes:
        - current: The actual text found (empty string for MISSING items)
        - is_highlightable: True if current text can be highlighted in CV
    """
    issues = []
    
    if not contact.has_email:
        issues.append({
            'issue_type': 'CONTACT_MISSING_EMAIL',
            'location': 'Contact Information',
            'description': 'No email address found in CV',
            'current': '',
            'is_highlightable': False,
        })
    elif not contact.email_valid:
        issues.append({
            'issue_type': 'CONTACT_UNPROFESSIONAL_EMAIL',
            'location': 'Contact Information',
            'description': f'Email format appears invalid: {contact.email}',
            'current': contact.email,
            'is_highlightable': True,
        })
    elif contact.email:
        unprofessional_reason = check_unprofessional_email(contact.email)
        if unprofessional_reason:
            issues.append({
                'issue_type': 'CONTACT_UNPROFESSIONAL_EMAIL',
                'location': 'Contact Information',
                'description': f'Email may appear unprofessional: {unprofessional_reason}',
                'current': contact.email,
                'is_highlightable': True,
            })
    
    if not contact.has_phone:
        issues.append({
            'issue_type': 'CONTACT_MISSING_PHONE',
            'location': 'Contact Information',
            'description': 'No phone number found in CV',
            'current': '',
            'is_highlightable': False,
        })
    elif not contact.phone_valid:
        issues.append({
            'issue_type': 'CONTACT_INCONSISTENT_FORMAT',
            'location': 'Contact Information',
            'description': f'Phone format appears invalid: {contact.phone}',
            'current': contact.phone,
            'is_highlightable': True,
        })
    
    if not contact.has_linkedin:
        linkedin_no_url_issues = detect_linkedin_no_url(full_text) if full_text else []
        if linkedin_no_url_issues:
            issues.extend(linkedin_no_url_issues)
        else:
            issues.append({
                'issue_type': 'CONTACT_MISSING_LINKEDIN',
                'location': 'Contact Information',
                'description': 'No LinkedIn profile URL found',
                'current': '',
                'is_highlightable': False,
            })
    
    if full_text:
        location = extract_location(full_text)
        if not location:
            issues.append({
                'issue_type': 'CONTACT_MISSING_LOCATION',
                'location': 'Contact Information',
                'description': 'No location (city, state) found in CV header',
                'current': '',
                'is_highlightable': False,
            })
        
        if is_tech_cv(full_text) and not contact.github:
            issues.append({
                'issue_type': 'CONTACT_MISSING_GITHUB',
                'location': 'Contact Information',
                'description': 'No GitHub profile found - recommended for technical roles',
                'current': '',
                'is_highlightable': False,
            })
        
        if check_photo_included(full_text):
            issues.append({
                'issue_type': 'CONTACT_PHOTO_INCLUDED',
                'location': 'Contact Information',
                'description': 'Photo indicator detected - photos may cause bias in US/UK hiring',
                'current': '[photo]',
                'is_highlightable': True,
            })
        
        mixed_separators = check_inconsistent_separators(full_text)
        if mixed_separators:
            issues.append({
                'issue_type': 'CONTACT_INCONSISTENT_FORMAT',
                'location': 'Contact Information',
                'description': f'Mixed separators in contact section: {", ".join(mixed_separators)}',
                'current': ', '.join(mixed_separators),
                'is_highlightable': False,
            })
    
    return issues
