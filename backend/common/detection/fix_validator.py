"""
Post-Fix Validation Module

Ensures AI fix didn't break critical CV elements like email, phone, LinkedIn.
If broken, restores them from the original CV.
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_PATTERN = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
LINKEDIN_PATTERN = r'linkedin\.com/in/[a-zA-Z0-9_-]+'
GITHUB_PATTERN = r'github\.com/[a-zA-Z0-9_-]+'


def extract_critical_elements(text: str) -> Dict[str, List[str]]:
    """
    Extract all critical contact elements from CV text.
    
    Args:
        text: CV text content
        
    Returns:
        Dictionary with lists of found elements
    """
    return {
        'emails': re.findall(EMAIL_PATTERN, text, re.IGNORECASE),
        'phones': re.findall(PHONE_PATTERN, text),
        'linkedin': re.findall(LINKEDIN_PATTERN, text, re.IGNORECASE),
        'github': re.findall(GITHUB_PATTERN, text, re.IGNORECASE)
    }


def validate_fix(original_text: str, fixed_text: str) -> Tuple[bool, List[str]]:
    """
    Validate that AI fix didn't remove or break critical elements.
    
    Args:
        original_text: Original CV text before fix
        fixed_text: Fixed CV text after AI processing
        
    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    original_elements = extract_critical_elements(original_text)
    fixed_elements = extract_critical_elements(fixed_text)
    
    warnings = []
    is_valid = True
    
    if original_elements['emails'] and not fixed_elements['emails']:
        warnings.append("Email address was removed or broken by fix")
        is_valid = False
        logger.warning(f"[FIX_VALIDATOR] Email broken: {original_elements['emails']}")
    
    if original_elements['phones'] and not fixed_elements['phones']:
        warnings.append("Phone number was removed or broken by fix")
        is_valid = False
        logger.warning(f"[FIX_VALIDATOR] Phone broken: {original_elements['phones']}")
    
    if original_elements['linkedin'] and not fixed_elements['linkedin']:
        warnings.append("LinkedIn URL was removed or broken by fix")
        is_valid = False
        logger.warning(f"[FIX_VALIDATOR] LinkedIn broken: {original_elements['linkedin']}")
    
    if original_elements['github'] and not fixed_elements['github']:
        warnings.append("GitHub URL was removed or broken by fix")
        is_valid = False
        logger.warning(f"[FIX_VALIDATOR] GitHub broken: {original_elements['github']}")
    
    if is_valid:
        logger.info("[FIX_VALIDATOR] All critical elements preserved")
    
    return is_valid, warnings


def restore_critical_elements(original_text: str, fixed_text: str) -> str:
    """
    Restore critical elements that AI accidentally broke.
    
    Args:
        original_text: Original CV text with correct elements
        fixed_text: Fixed CV text with possibly broken elements
        
    Returns:
        Fixed text with critical elements restored
    """
    original_elements = extract_critical_elements(original_text)
    fixed_elements = extract_critical_elements(fixed_text)
    
    result = fixed_text
    restorations = []
    
    if original_elements['emails'] and not fixed_elements['emails']:
        original_email = original_elements['emails'][0]
        placeholders = [
            r'\[Email\s*Address?\]',
            r'\[Your\s*Email\]',
            r'\[Email\]',
            r'\[email\]',
            r'email\s*address\s*here',
        ]
        for placeholder in placeholders:
            if re.search(placeholder, result, re.IGNORECASE):
                result = re.sub(placeholder, original_email, result, flags=re.IGNORECASE)
                restorations.append(f"Restored email: {original_email}")
                break
    
    if original_elements['phones'] and not fixed_elements['phones']:
        original_phone = original_elements['phones'][0]
        placeholders = [
            r'\[Phone\s*Number?\]',
            r'\[Your\s*Phone\]',
            r'\[Phone\]',
            r'\[phone\]',
            r'phone\s*number\s*here',
        ]
        for placeholder in placeholders:
            if re.search(placeholder, result, re.IGNORECASE):
                result = re.sub(placeholder, original_phone, result, flags=re.IGNORECASE)
                restorations.append(f"Restored phone: {original_phone}")
                break
    
    if original_elements['linkedin'] and not fixed_elements['linkedin']:
        original_linkedin = original_elements['linkedin'][0]
        placeholders = [
            r'\[LinkedIn\s*Profile\s*URL?\]',
            r'\[Your\s*LinkedIn\]',
            r'\[LinkedIn\s*URL\]',
            r'\[LinkedIn\]',
            r'\[linkedin\]',
            r'linkedin\s*profile\s*url',
        ]
        for placeholder in placeholders:
            if re.search(placeholder, result, re.IGNORECASE):
                result = re.sub(placeholder, original_linkedin, result, flags=re.IGNORECASE)
                restorations.append(f"Restored LinkedIn: {original_linkedin}")
                break
    
    if original_elements['github'] and not fixed_elements['github']:
        original_github = original_elements['github'][0]
        placeholders = [
            r'\[GitHub\s*Profile\s*URL?\]',
            r'\[Your\s*GitHub\]',
            r'\[GitHub\s*URL\]',
            r'\[GitHub\]',
            r'\[github\]',
        ]
        for placeholder in placeholders:
            if re.search(placeholder, result, re.IGNORECASE):
                result = re.sub(placeholder, original_github, result, flags=re.IGNORECASE)
                restorations.append(f"Restored GitHub: {original_github}")
                break
    
    if restorations:
        logger.info(f"[FIX_VALIDATOR] Restorations made: {restorations}")
    
    return result
