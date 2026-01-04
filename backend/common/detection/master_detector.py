"""
Master Detector - Orchestrates All Static Detection

This is the SINGLE ENTRY POINT for CV issue detection.
Runs all static detectors and combines results.

100% CODE detection - AI is NOT used here.
Same CV text → Same issues → Same results (ALWAYS)
"""

import logging
from typing import List, Dict, Any

from common.catalog import get_catalog_service
from .contact_extractor import extract_contact_info, get_contact_issues
from .section_extractor import (
    extract_sections, 
    get_section_issues, 
    get_cv_length_issues,
    get_experience_detail_issues,
    get_education_detail_issues,
)
from .bullet_extractor import extract_bullets, get_bullet_issues, get_bullets_per_job_issues
# from .spelling_detector import detect_critical_issues  # DISABLED - GRAMMAR_* issues inactive
from .language_detector import detect_language_issues
from .format_detector import detect_format_issues
from .polish_detector import detect_polish_issues
from .standards_detector import detect_standards_issues
from .keywords_detector import detect_keywords_issues
from .structure_detector import detect_structure_issues
from .skills_detector import detect_all_skills_issues
from .length_detector import (
    detect_summary_too_long,
    detect_job_description_too_short,
    detect_job_description_too_long,
    detect_education_description_too_short,
    detect_job_description_issues_simple
)
from .abbreviation_detector import detect_all_abbreviation_issues
from .certification_detector import detect_all_certification_issues

logger = logging.getLogger(__name__)


def enrich_issues_from_catalog(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich detected issues with metadata from the catalog.
    This replaces the old ISSUE_TYPE_CONFIG lookup.
    """
    try:
        catalog_service = get_catalog_service()
        if catalog_service.is_ready:
            return catalog_service.enrich_all_issues(issues)
    except Exception as e:
        logger.warning(f"Could not enrich from catalog: {e}")
    
    return issues


def detect_all_issues(cv_text: str, job_description: str = None) -> List[Dict[str, Any]]:
    """
    Run ALL static detectors on CV text.
    
    This is the MAIN function - call this to get all issues.
    
    DETERMINISTIC: Same cv_text → Same issues (ALWAYS)
    
    Args:
        cv_text: Full CV text content
        job_description: Optional job description for keyword matching
        
    Returns:
        List of issue dictionaries, each with:
        - issue_type: str (e.g., 'GRAMMAR_SPELLING_ERROR', 'CONTENT_MISSING_METRICS')
        - location: str (where in CV)
        - description: str (what's wrong)
        - current: str (optional - current problematic text)
        - suggestion: str (optional - how to fix)
    """
    all_issues: List[Dict[str, Any]] = []
    structure = None
    
    logger.info("Starting static CV analysis...")
    
    # DISABLED: Spelling/grammar detector - all GRAMMAR_* issues are is_active=false in catalog
    # The spelling detector was generating too many low-value issues.
    # To re-enable, uncomment the block below and ensure GRAMMAR_* issues are active in catalog.
    # try:
    #     critical_issues = detect_critical_issues(cv_text)
    #     all_issues.extend(critical_issues)
    #     logger.info(f"Critical issues found: {len(critical_issues)}")
    # except Exception as e:
    #     logger.error(f"Error detecting critical issues: {e}")
    
    try:
        contact_info = extract_contact_info(cv_text)
        contact_issues = get_contact_issues(contact_info, cv_text)
        all_issues.extend(contact_issues)
        logger.info(f"Contact issues found: {len(contact_issues)}")
    except Exception as e:
        logger.error(f"Error detecting contact issues: {e}")
    
    try:
        structure = extract_sections(cv_text)
        section_issues = get_section_issues(structure)
        all_issues.extend(section_issues)
        logger.info(f"Section issues found: {len(section_issues)}")
        
        length_issues = get_cv_length_issues(cv_text)
        all_issues.extend(length_issues)
        
        experience_detail_issues = get_experience_detail_issues(cv_text)
        all_issues.extend(experience_detail_issues)
        
        education_detail_issues = get_education_detail_issues(structure)
        all_issues.extend(education_detail_issues)
    except Exception as e:
        logger.error(f"Error detecting section issues: {e}")
    
    try:
        experience_text = structure.experience if structure and structure.experience else cv_text
        bullets = extract_bullets(experience_text)
        bullet_issues = get_bullet_issues(bullets)
        all_issues.extend(bullet_issues)
        logger.info(f"Bullet issues found: {len(bullet_issues)}")
        
        bullets_per_job_issues = get_bullets_per_job_issues(cv_text)
        all_issues.extend(bullets_per_job_issues)
    except Exception as e:
        logger.error(f"Error detecting bullet issues: {e}")
    
    try:
        language_issues = detect_language_issues(cv_text)
        all_issues.extend(language_issues)
        logger.info(f"Language issues found: {len(language_issues)}")
    except Exception as e:
        logger.error(f"Error detecting language issues: {e}")
    
    try:
        format_issues = detect_format_issues(cv_text)
        all_issues.extend(format_issues)
        logger.info(f"Format issues found: {len(format_issues)}")
    except Exception as e:
        logger.error(f"Error detecting format issues: {e}")
    
    try:
        polish_issues = detect_polish_issues(cv_text)
        all_issues.extend(polish_issues)
        logger.info(f"Polish issues found: {len(polish_issues)}")
    except Exception as e:
        logger.error(f"Error detecting polish issues: {e}")
    
    try:
        standards_issues = detect_standards_issues(cv_text)
        all_issues.extend(standards_issues)
        logger.info(f"Standards issues found: {len(standards_issues)}")
    except Exception as e:
        logger.error(f"Error detecting standards issues: {e}")
    
    try:
        keywords_issues = detect_keywords_issues(cv_text, job_description)
        all_issues.extend(keywords_issues)
        logger.info(f"Keywords issues found: {len(keywords_issues)}")
    except Exception as e:
        logger.error(f"Error detecting keywords issues: {e}")
    
    try:
        structure_issues = detect_structure_issues(cv_text)
        all_issues.extend(structure_issues)
        logger.info(f"Structure issues found: {len(structure_issues)}")
    except Exception as e:
        logger.error(f"Error detecting structure issues: {e}")
    
    # Skills Section Detection (v1.4)
    try:
        skills_issues = detect_all_skills_issues(cv_text)
        all_issues.extend(skills_issues)
        logger.info(f"Skills issues found: {len(skills_issues)}")
    except Exception as e:
        logger.error(f"Error detecting skills issues: {e}")
    
    # Length-Based Detection (v1.5)
    try:
        # Summary length detection - structure.summary is available as raw text
        if structure and structure.summary:
            summary_issues = detect_summary_too_long(structure.summary)
            all_issues.extend(summary_issues)
            logger.info(f"Summary length issues found: {len(summary_issues)}")
        
        # Job Description Length Detection (Simple) - works with raw experience text
        if structure and structure.experience:
            job_desc_issues = detect_job_description_issues_simple(structure.experience)
            all_issues.extend(job_desc_issues)
            logger.info(f"Job description length issues found: {len(job_desc_issues)}")
        
        # Note: Education length detector requires parsed entries
        # in List[Dict] format (institution/degree/description).
        # TODO: Add education parsing function to enable:
        # - detect_education_description_too_short(education_entries, years_experience)
    except Exception as e:
        logger.error(f"Error detecting length issues: {e}")
    
    # Abbreviation consistency detection
    try:
        abbreviation_issues = detect_all_abbreviation_issues(cv_text)
        all_issues.extend(abbreviation_issues)
        logger.info(f"Abbreviation issues found: {len(abbreviation_issues)}")
    except Exception as e:
        logger.error(f"Error detecting abbreviation issues: {e}")
    
    # Certification count detection
    try:
        certification_issues = detect_all_certification_issues(cv_text)
        all_issues.extend(certification_issues)
        logger.info(f"Certification issues found: {len(certification_issues)}")
    except Exception as e:
        logger.error(f"Error detecting certification issues: {e}")
    
    logger.info(f"Static detection complete. Total issues: {len(all_issues)}")
    
    all_issues = enrich_issues_from_catalog(all_issues)
    
    return all_issues


def get_detection_summary(issues: List[Dict]) -> Dict[str, int]:
    """
    Get summary counts by issue type.
    
    Args:
        issues: List of issues from detect_all_issues
        
    Returns:
        Dictionary with counts per issue_type
    """
    from collections import Counter
    
    types = [issue.get('issue_type', 'UNKNOWN') for issue in issues]
    return dict(Counter(types))
