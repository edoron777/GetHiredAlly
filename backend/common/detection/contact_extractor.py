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


def get_contact_issues(contact: ContactInfo) -> List[Dict]:
    """
    Generate issues based on contact info extraction.
    
    Returns list of issue dictionaries with issue_type.
    """
    issues = []
    
    if not contact.has_email:
        issues.append({
            'issue_type': 'MISSING_EMAIL',
            'location': 'Contact Information',
            'description': 'No email address found in CV',
        })
    elif not contact.email_valid:
        issues.append({
            'issue_type': 'INVALID_EMAIL',
            'location': 'Contact Information',
            'description': f'Email format appears invalid: {contact.email}',
            'current': contact.email,
        })
    
    if not contact.has_phone:
        issues.append({
            'issue_type': 'MISSING_PHONE',
            'location': 'Contact Information',
            'description': 'No phone number found in CV',
        })
    elif not contact.phone_valid:
        issues.append({
            'issue_type': 'INVALID_PHONE',
            'location': 'Contact Information',
            'description': f'Phone format appears invalid: {contact.phone}',
            'current': contact.phone,
        })
    
    if not contact.has_linkedin:
        issues.append({
            'issue_type': 'MISSING_LINKEDIN',
            'location': 'Contact Information',
            'description': 'No LinkedIn profile URL found',
        })
    
    return issues
