"""
Job Hopping Detector

Identifies candidates with multiple short-term positions.
Short-term = less than 12 months at a job.

Red flags:
- 3+ jobs lasting < 12 months = Important
- 2 jobs lasting < 12 months = Consider

Also detects employment gaps.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    relativedelta = None

try:
    from common.detection.block_detector import CVBlockStructure
except ImportError:
    CVBlockStructure = None


def parse_date_range(date_string: str) -> Tuple[Optional[datetime], Optional[datetime], bool]:
    """
    Parse date range from various formats.
    
    Handles:
    - "Jan 2020 - Dec 2022"
    - "January 2020 - Present"
    - "2020 - 2022"
    - "01/2020 - 12/2022"
    
    Returns: (start_date, end_date, is_current)
    """
    if not date_string:
        return None, None, False
    
    is_current = any(word in date_string.lower() for word in ['present', 'current', 'now', 'ongoing'])
    
    month_map = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'sept': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12,
    }
    
    date_pattern = r'(?:(\w+)\s*)?(\d{4})'
    matches = re.findall(date_pattern, date_string, re.IGNORECASE)
    
    if len(matches) >= 1:
        month_str, year_str = matches[0]
        start_month = month_map.get(month_str.lower(), 1) if month_str else 1
        start_year = int(year_str)
        start_date = datetime(start_year, start_month, 1)
        
        if is_current:
            end_date = datetime.now()
        elif len(matches) >= 2:
            month_str, year_str = matches[1]
            end_month = month_map.get(month_str.lower(), 12) if month_str else 12
            end_year = int(year_str)
            end_date = datetime(end_year, end_month, 1)
        else:
            end_date = None
            
        return start_date, end_date, is_current
    
    return None, None, False


def calculate_tenure_months(start_date: datetime, end_date: datetime) -> int:
    """Calculate months between two dates."""
    if not start_date or not end_date:
        return 0
    
    if relativedelta:
        delta = relativedelta(end_date, start_date)
        return delta.years * 12 + delta.months
    else:
        days = (end_date - start_date).days
        return days // 30


def extract_job_dates_from_text(cv_text: str) -> List[Dict]:
    """
    Extract job entries with dates from CV text.
    
    Returns list of jobs with start_date, end_date, tenure_months
    """
    jobs = []
    
    date_patterns = [
        r'(\w+\s+\d{4})\s*[-–—to]+\s*(\w+\s+\d{4}|[Pp]resent|[Cc]urrent|[Nn]ow)',
        r'(\d{4})\s*[-–—to]+\s*(\d{4}|[Pp]resent|[Cc]urrent|[Nn]ow)',
        r'(\d{1,2}/\d{4})\s*[-–—to]+\s*(\d{1,2}/\d{4}|[Pp]resent|[Cc]urrent)',
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, cv_text)
        for match in matches:
            date_string = f"{match[0]} - {match[1]}"
            start_date, end_date, is_current = parse_date_range(date_string)
            
            if start_date and end_date:
                tenure = calculate_tenure_months(start_date, end_date)
                jobs.append({
                    "date_range": date_string,
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_current": is_current,
                    "tenure_months": tenure,
                })
    
    seen = set()
    unique_jobs = []
    for job in jobs:
        key = (job["start_date"], job["end_date"])
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    unique_jobs.sort(key=lambda x: x["start_date"], reverse=True)
    
    return unique_jobs


def detect_employment_gaps(cv_text: str, cv_block_structure: Optional['CVBlockStructure'] = None) -> List[Dict]:
    """
    Detect gaps in employment history.
    
    Rules:
    - Gap = time between end of one job and start of next
    - Gap > 3 months = Worth mentioning
    - Gap > 6 months = Important issue
    - Gap > 12 months = Critical concern
    
    Returns list of issues found.
    """
    issues = []
    
    jobs = extract_job_dates_from_text(cv_text)
    
    if len(jobs) < 2:
        return issues
    
    jobs_sorted = sorted(jobs, key=lambda x: x["start_date"])
    
    gaps_found = []
    
    for i in range(len(jobs_sorted) - 1):
        current_job = jobs_sorted[i]
        next_job = jobs_sorted[i + 1]
        
        if current_job["end_date"] and next_job["start_date"]:
            gap_months = calculate_tenure_months(current_job["end_date"], next_job["start_date"])
            
            if gap_months > 3:
                gaps_found.append({
                    "gap_months": gap_months,
                    "from_date": current_job["end_date"].strftime("%B %Y"),
                    "to_date": next_job["start_date"].strftime("%B %Y"),
                    "between": f"between {current_job['date_range']} and {next_job['date_range']}"
                })
    
    if not gaps_found:
        return issues
    
    max_gap = max(g["gap_months"] for g in gaps_found)
    total_gaps = len(gaps_found)
    
    if max_gap > 12:
        severity = "important"
    elif max_gap > 6:
        severity = "important"
    else:
        severity = "consider"
    
    if total_gaps == 1:
        gap = gaps_found[0]
        description = f"Employment gap of {gap['gap_months']} months detected ({gap['from_date']} to {gap['to_date']}). Consider adding a brief explanation."
    else:
        gap_list = ", ".join([f"{g['gap_months']} months" for g in gaps_found])
        description = f"{total_gaps} employment gaps detected ({gap_list}). Unexplained gaps may raise concerns with recruiters."
    
    issues.append({
        "issue_type": "CAREER_EMPLOYMENT_GAP",
        "severity": severity,
        "match_text": f"{total_gaps} gap(s) totaling {sum(g['gap_months'] for g in gaps_found)} months",
        "suggestion": "Add brief explanations for employment gaps (career break, education, freelance work, etc.)",
        "can_auto_fix": False,
        "details": {
            "gaps": gaps_found,
            "total_gaps": total_gaps,
            "max_gap_months": max_gap,
        },
        "line_number": None,
    })
    
    return issues


def detect_job_hopping(cv_text: str, cv_block_structure: Optional['CVBlockStructure'] = None) -> List[Dict]:
    """
    Detect job hopping pattern in CV.
    
    Rules:
    - Job lasting < 12 months = short-term
    - 3+ short-term jobs = Important issue
    - 2 short-term jobs = Consider issue
    - Current job excluded (they just started)
    
    Returns list of issues found.
    """
    issues = []
    
    jobs = extract_job_dates_from_text(cv_text)
    
    if not jobs:
        return issues
    
    short_term_jobs = []
    for job in jobs:
        if job["is_current"]:
            continue
        
        if job["tenure_months"] < 12:
            short_term_jobs.append(job)
    
    short_count = len(short_term_jobs)
    
    if short_count >= 3:
        job_list = ", ".join([
            f"{job['date_range']} ({job['tenure_months']} months)" 
            for job in short_term_jobs[:5]
        ])
        
        issues.append({
            "issue_type": "CAREER_JOB_HOPPING",
            "severity": "important",
            "match_text": f"{short_count} positions lasting less than 1 year",
            "suggestion": "Consider grouping short-term roles as 'Contract Work' or add brief explanations for each departure",
            "can_auto_fix": False,
            "details": {
                "short_term_count": short_count,
                "jobs": [{"date_range": j["date_range"], "tenure_months": j["tenure_months"]} for j in short_term_jobs],
            },
            "line_number": None,
        })
        
    elif short_count == 2:
        job_list = ", ".join([
            f"{job['date_range']} ({job['tenure_months']} months)" 
            for job in short_term_jobs
        ])
        
        issues.append({
            "issue_type": "CAREER_JOB_HOPPING",
            "severity": "consider",
            "match_text": "2 positions lasting less than 1 year",
            "suggestion": "Consider adding context for short tenures (contract work, company closure, etc.)",
            "can_auto_fix": False,
            "details": {
                "short_term_count": short_count,
                "jobs": [{"date_range": j["date_range"], "tenure_months": j["tenure_months"]} for j in short_term_jobs],
            },
            "line_number": None,
        })
    
    return issues


def detect_career_issues(cv_text: str, cv_block_structure: Optional['CVBlockStructure'] = None) -> List[Dict]:
    """
    Main entry point for career pattern detection.
    Includes:
    - Employment gaps (unexplained periods between jobs)
    - Job hopping (multiple short-term positions)
    """
    issues = []
    
    issues.extend(detect_employment_gaps(cv_text, cv_block_structure))
    issues.extend(detect_job_hopping(cv_text, cv_block_structure))
    
    return issues


def detect_all_career_issues(cv_text: str, cv_block_structure: Optional['CVBlockStructure'] = None) -> List[Dict]:
    """Alias for detect_career_issues for consistency with other detectors."""
    return detect_career_issues(cv_text, cv_block_structure)
