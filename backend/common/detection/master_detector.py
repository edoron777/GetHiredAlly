"""
Master Detector - Orchestrates All Static Detection

This is the SINGLE ENTRY POINT for CV issue detection.
Runs all static detectors and combines results.

100% CODE detection - AI is NOT used here.
Same CV text → Same issues → Same results (ALWAYS)
"""

import re
import logging
from typing import List, Dict, Any, Optional

from common.catalog import get_catalog_service


def validate_issue_format(issue: Dict[str, Any], cv_text: str = '') -> Dict[str, Any]:
    """
    Validate and fix issue format before returning.
    Ensures 'current' field is properly populated for highlighting.
    
    Args:
        issue: The issue dictionary to validate
        cv_text: Original CV text to verify current field exists in it
        
    Returns:
        Validated issue dictionary
    """
    if 'issue_type' not in issue:
        issue['issue_type'] = 'UNKNOWN'
    
    current = issue.get('current', '')
    
    if current:
        if '...' in current:
            current = current.replace('...', '').strip()
        
        invalid_patterns = [
            r'^\d+\s*words?$',
            r'^\d+\s*characters?$',
            r'^Line\s*\d+',
            r'^\d+\s*months?\s*gap',
            r'^\d+\s*bullets?$',
        ]
        for pattern in invalid_patterns:
            if re.match(pattern, current, re.IGNORECASE):
                current = ''
                break
        
        if current and len(current) > 200:
            current = current[:200]
        
        if current and cv_text and current not in cv_text:
            current = ''
    
    issue['current'] = current
    
    if 'is_highlightable' not in issue:
        issue['is_highlightable'] = bool(current and len(current) >= 3)
    elif current == '':
        issue['is_highlightable'] = False
    
    return issue


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

# Block structure detection (Phase 2 - CV Detection Refactoring)
from .block_detector import (
    detect_cv_blocks,
    CVBlockStructure,
    BlockType,
    get_experience_text,
    get_education_text,
    get_summary_text,
    get_skills_text,
)

# ═══════════════════════════════════════════════════════════════════════════════
# CV ISSUE REPORT - Main output of detect_cv_issues()
# ═══════════════════════════════════════════════════════════════════════════════

from dataclasses import dataclass, field


@dataclass
class IssueReportSummary:
    """Summary statistics for the CV issue report."""
    
    # Counts
    total_issues: int = 0
    critical_count: int = 0
    major_count: int = 0
    minor_count: int = 0
    suggestion_count: int = 0
    
    # By category
    language_issues: int = 0
    format_issues: int = 0
    content_issues: int = 0
    structure_issues: int = 0
    length_issues: int = 0
    
    # Score (0-100)
    overall_score: int = 100
    
    # Flags
    has_critical_issues: bool = False
    auto_fixable_count: int = 0


@dataclass
class CVIssueReport:
    """
    Complete report of all CV issues detected.
    
    This is the main output of detect_cv_issues() function.
    It wraps all detected issues with organization and statistics.
    """
    
    # All issues (List[Dict] format for backward compatibility)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    
    # Organized views
    issues_by_category: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    issues_by_severity: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    
    # Summary statistics
    summary: IssueReportSummary = field(default_factory=IssueReportSummary)
    
    # The CV structure used (for reference)
    cv_structure: Optional[CVBlockStructure] = None
    
    # Metadata
    processing_time_ms: float = 0.0
    detector_errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'issues': self.issues,
            'issues_by_category': self.issues_by_category,
            'issues_by_severity': self.issues_by_severity,
            'summary': {
                'total_issues': self.summary.total_issues,
                'critical_count': self.summary.critical_count,
                'major_count': self.summary.major_count,
                'minor_count': self.summary.minor_count,
                'suggestion_count': self.summary.suggestion_count,
                'overall_score': self.summary.overall_score,
                'has_critical_issues': self.summary.has_critical_issues,
                'auto_fixable_count': self.summary.auto_fixable_count,
            },
            'processing_time_ms': self.processing_time_ms,
            'detector_errors': self.detector_errors,
        }
    
    def get_issues_for_block(self, block_type: BlockType) -> List[Dict[str, Any]]:
        """Get all issues for a specific block type."""
        block_name = block_type.value.lower()
        return [i for i in self.issues if i.get('location', '').lower().find(block_name) >= 0]
    
    def get_auto_fixable_issues(self) -> List[Dict[str, Any]]:
        """Get all issues that can be auto-fixed."""
        return [i for i in self.issues if i.get('can_auto_fix', False)]


logger = logging.getLogger(__name__)

import os

USE_NEW_ENGINE = os.environ.get('CV_USE_NEW_DETECTION_ENGINE', 'false').lower() == 'true'
PARALLEL_MODE = os.environ.get('CV_DETECTION_PARALLEL_MODE', 'false').lower() == 'true'

_rule_engine = None

def _get_rule_engine():
    """Lazy initialization of RuleEngine."""
    global _rule_engine
    if _rule_engine is None:
        try:
            from .rule_engine import get_rule_engine
            _rule_engine = get_rule_engine()
        except Exception as e:
            logger.error(f"Failed to initialize RuleEngine: {e}")
    return _rule_engine


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


def detect_all_issues(cv_text: str, job_description: Optional[str] = None) -> List[Dict[str, Any]]:
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
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 2: CV BLOCK STRUCTURE DETECTION
    # Call detect_cv_blocks() FIRST to get structured CV representation
    # This provides line numbers, job boundaries, and section metadata
    # ═══════════════════════════════════════════════════════════════════════
    
    cv_block_structure: Optional[CVBlockStructure] = None
    try:
        cv_block_structure = detect_cv_blocks(cv_text)
        if cv_block_structure and cv_block_structure.errors:
            for error in cv_block_structure.errors:
                logger.warning(f"[block_detector] {error}")
    except Exception as e:
        logger.error(f"[block_detector] Error: {str(e)} - continuing with raw text")
        cv_block_structure = None
    
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
        
        length_issues = get_cv_length_issues(cv_text, cv_block_structure=cv_block_structure)
        all_issues.extend(length_issues)
        
        experience_detail_issues = get_experience_detail_issues(cv_text, cv_block_structure=cv_block_structure)
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
        
        bullets_per_job_issues = get_bullets_per_job_issues(cv_text, cv_block_structure=cv_block_structure)
        all_issues.extend(bullets_per_job_issues)
    except Exception as e:
        logger.error(f"Error detecting bullet issues: {e}")
    
    try:
        language_issues = detect_language_issues(cv_text, cv_block_structure=cv_block_structure)
        all_issues.extend(language_issues)
        logger.info(f"Language issues found: {len(language_issues)}")
    except Exception as e:
        logger.error(f"Error detecting language issues: {e}")
    
    try:
        format_issues = detect_format_issues(cv_text, cv_block_structure=cv_block_structure)
        all_issues.extend(format_issues)
        logger.info(f"Format issues found: {len(format_issues)}")
    except Exception as e:
        logger.error(f"Error detecting format issues: {e}")
    
    try:
        polish_issues = detect_polish_issues(cv_text, cv_block_structure=cv_block_structure)
        all_issues.extend(polish_issues)
        logger.info(f"Polish issues found: {len(polish_issues)}")
    except Exception as e:
        logger.error(f"Error detecting polish issues: {e}")
    
    try:
        standards_issues = detect_standards_issues(cv_text, cv_block_structure=cv_block_structure)
        all_issues.extend(standards_issues)
        logger.info(f"Standards issues found: {len(standards_issues)}")
    except Exception as e:
        logger.error(f"Error detecting standards issues: {e}")
    
    try:
        keywords_issues = detect_keywords_issues(cv_text, job_description, cv_block_structure=cv_block_structure)
        all_issues.extend(keywords_issues)
        logger.info(f"Keywords issues found: {len(keywords_issues)}")
    except Exception as e:
        logger.error(f"Error detecting keywords issues: {e}")
    
    try:
        structure_issues = detect_structure_issues(cv_text, cv_block_structure=cv_block_structure)
        all_issues.extend(structure_issues)
        logger.info(f"Structure issues found: {len(structure_issues)}")
    except Exception as e:
        logger.error(f"Error detecting structure issues: {e}")
    
    # Skills Section Detection (v1.4)
    try:
        skills_issues = detect_all_skills_issues(cv_text, cv_block_structure=cv_block_structure)
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
        abbreviation_issues = detect_all_abbreviation_issues(cv_text, cv_block_structure=cv_block_structure)
        all_issues.extend(abbreviation_issues)
        logger.info(f"Abbreviation issues found: {len(abbreviation_issues)}")
    except Exception as e:
        logger.error(f"Error detecting abbreviation issues: {e}")
    
    # Certification count detection
    try:
        certification_issues = detect_all_certification_issues(cv_text, cv_block_structure=cv_block_structure)
        all_issues.extend(certification_issues)
        logger.info(f"Certification issues found: {len(certification_issues)}")
    except Exception as e:
        logger.error(f"Error detecting certification issues: {e}")
    
    logger.info(f"Static detection complete. Total issues: {len(all_issues)}")
    
    all_issues = [validate_issue_format(issue, cv_text) for issue in all_issues]
    
    all_issues = enrich_issues_from_catalog(all_issues)
    
    if PARALLEL_MODE or USE_NEW_ENGINE:
        try:
            rule_engine = _get_rule_engine()
            if rule_engine:
                new_issues = rule_engine.detect_all_issues(cv_text)
                
                if PARALLEL_MODE and not USE_NEW_ENGINE:
                    old_codes = set(i.get('issue_type') or i.get('issue_code') for i in all_issues)
                    new_codes = set(i.get('issue_type') or i.get('issue_code') for i in new_issues)
                    
                    only_old = old_codes - new_codes
                    only_new = new_codes - old_codes
                    common = old_codes & new_codes
                    
                    logger.info(f"[PARALLEL MODE] Detection comparison:")
                    logger.info(f"  - Old engine: {len(old_codes)} issues")
                    logger.info(f"  - New engine: {len(new_codes)} issues")
                    logger.info(f"  - Common: {len(common)}")
                    logger.info(f"  - Only in old: {only_old}")
                    logger.info(f"  - Only in new: {only_new}")
                
                if USE_NEW_ENGINE:
                    logger.info(f"[NEW ENGINE] Using database-driven detection: {len(new_issues)} issues")
                    return new_issues
                    
        except Exception as e:
            logger.error(f"New detection engine error: {e}", exc_info=True)
    
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


def enrich_issues_with_line_numbers(
    issues: List[Dict[str, Any]],
    cv_block_structure: Optional[CVBlockStructure],
    cv_text: str
) -> List[Dict[str, Any]]:
    """
    Enrich issues with line numbers by finding where 'current' text appears.
    
    Uses cv_block_structure to:
    1. Find which block contains the issue text
    2. Get the line number from that block
    3. Add block_type and job_index for context
    
    Args:
        issues: List of issue dicts
        cv_block_structure: The CV structure with line numbers
        cv_text: Original CV text (for fallback line search)
    
    Returns:
        Same issues list with line_number, block_type, job_index added
    """
    if not cv_block_structure:
        return issues
    
    # Build a line lookup from CV text
    lines = cv_text.split('\n')
    
    for issue in issues:
        current = issue.get('current', '')
        if not current or len(current) < 3:
            continue
        
        # Try to find line number
        line_number = None
        block_type = None
        job_index = None
        
        # Method 1: Search in blocks
        for block in cv_block_structure.blocks:
            if current in block.content:
                line_number = block.start_line
                block_type = block.block_type.value
                
                # If it's an experience block, find which job
                if block.block_type == BlockType.EXPERIENCE:
                    for idx, job in enumerate(cv_block_structure.all_jobs):
                        if current in job.raw_text:
                            job_index = idx
                            # More precise line number from job
                            if job.start_line:
                                line_number = job.start_line
                            break
                
                # Search for exact line within block
                for i, line in enumerate(lines[block.start_line - 1:block.end_line], start=block.start_line):
                    if current in line:
                        line_number = i
                        break
                
                break
        
        # Method 2: Fallback - search entire CV
        if line_number is None:
            for i, line in enumerate(lines, start=1):
                if current in line:
                    line_number = i
                    break
        
        # Update issue
        if line_number:
            issue['line_number'] = line_number
        if block_type:
            issue['block_type'] = block_type
        if job_index is not None:
            issue['job_index'] = job_index
    
    return issues


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT: detect_cv_issues()
# ═══════════════════════════════════════════════════════════════════════════════

def detect_cv_issues(
    cv_text: str,
    job_description: Optional[str] = None,
    cv_block_structure: Optional[CVBlockStructure] = None
) -> CVIssueReport:
    """
    Main entry point for CV issue detection.
    
    This function detects all issues/problems in a CV and returns
    a structured report with categorization and statistics.
    
    Args:
        cv_text: Raw CV text content
        job_description: Optional job description for keyword matching
        cv_block_structure: Optional pre-computed CV structure (for efficiency)
    
    Returns:
        CVIssueReport with:
        - issues: List of all detected issues
        - issues_by_category: Issues grouped by category
        - issues_by_severity: Issues grouped by severity
        - summary: Statistics and counts
        - cv_structure: The CVBlockStructure used
    
    Usage:
        # Simple usage
        report = detect_cv_issues(cv_text)
        
        # With job description
        report = detect_cv_issues(cv_text, job_description=job_desc)
        
        # With pre-computed structure (efficiency)
        structure = detect_cv_blocks(cv_text)
        report = detect_cv_issues(cv_text, cv_block_structure=structure)
    """
    import time
    start_time = time.time()
    
    # Initialize report
    report = CVIssueReport()
    
    try:
        # Step 1: Get or create CV block structure
        if cv_block_structure is None:
            try:
                from .block_detector import detect_cv_blocks
                cv_block_structure = detect_cv_blocks(cv_text)
            except Exception as e:
                report.detector_errors.append(f"block_detector: {str(e)}")
                cv_block_structure = None
        
        report.cv_structure = cv_block_structure
        
        # Step 2: Call existing detect_all_issues()
        # This runs all 17 detectors and returns List[Dict]
        all_issues = detect_all_issues(cv_text, job_description)
        report.issues = all_issues
        
        # Step 3: Organize issues by category
        report.issues_by_category = _organize_by_category(all_issues)
        
        # Step 4: Organize issues by severity
        report.issues_by_severity = _organize_by_severity(all_issues)
        
        # Step 5: Calculate summary statistics
        report.summary = _calculate_summary(all_issues)
        
    except Exception as e:
        report.detector_errors.append(f"detect_cv_issues: {str(e)}")
        logger.error(f"Error in detect_cv_issues: {str(e)}")
    
    # Record processing time
    report.processing_time_ms = (time.time() - start_time) * 1000
    
    return report


def _organize_by_category(issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Organize issues by category based on issue_type prefix."""
    categories = {}
    
    for issue in issues:
        issue_type = issue.get('issue_type', 'UNKNOWN')
        
        # Extract category from issue_type (e.g., "CONTENT_MISSING_SUMMARY" -> "content")
        if '_' in issue_type:
            category = issue_type.split('_')[0].lower()
        else:
            category = 'other'
        
        if category not in categories:
            categories[category] = []
        categories[category].append(issue)
    
    return categories


def _organize_by_severity(issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Organize issues by severity level."""
    severities = {
        'critical': [],
        'major': [],
        'minor': [],
        'suggestion': []
    }
    
    for issue in issues:
        severity = issue.get('severity', 'minor').lower()
        if severity not in severities:
            severity = 'minor'
        severities[severity].append(issue)
    
    return severities


def _calculate_summary(issues: List[Dict[str, Any]]) -> IssueReportSummary:
    """Calculate summary statistics from issues list."""
    summary = IssueReportSummary()
    summary.total_issues = len(issues)
    
    for issue in issues:
        # Count by severity
        severity = issue.get('severity', 'minor').lower()
        if severity == 'critical':
            summary.critical_count += 1
            summary.has_critical_issues = True
        elif severity == 'major':
            summary.major_count += 1
        elif severity == 'minor':
            summary.minor_count += 1
        else:
            summary.suggestion_count += 1
        
        # Count by category
        issue_type = issue.get('issue_type', '')
        if issue_type.startswith('CONTENT_'):
            if 'LANGUAGE' in issue_type or 'VERB' in issue_type:
                summary.language_issues += 1
            else:
                summary.content_issues += 1
        elif issue_type.startswith('FORMAT_'):
            summary.format_issues += 1
        elif issue_type.startswith('LENGTH_'):
            summary.length_issues += 1
        elif issue_type.startswith('STRUCTURE_'):
            summary.structure_issues += 1
        
        # Count auto-fixable
        if issue.get('can_auto_fix', False):
            summary.auto_fixable_count += 1
    
    # Calculate score (simple formula: 100 - weighted issues)
    # Critical = -15, Major = -8, Minor = -3, Suggestion = -1
    deductions = (
        summary.critical_count * 15 +
        summary.major_count * 8 +
        summary.minor_count * 3 +
        summary.suggestion_count * 1
    )
    summary.overall_score = max(0, min(100, 100 - deductions))
    
    return summary
