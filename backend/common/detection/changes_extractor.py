"""
Code-Based Changes Extraction Module

Purpose: Generate human-readable list of changes made during Auto-Fix
         WITHOUT using AI - 100% deterministic

Replaces: AI-based changes extraction in cv_optimizer.py (lines 1085-1115)
Cost: $0.00 (was ~$0.005-0.01 per call)

Output Format: Must match the JSON structure expected by frontend:
- CVFixedPage.tsx
- SideBySideView.tsx

Author: GetHiredAlly
Date: January 2026
"""

from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher, unified_diff
import re


def extract_changes_code_based(
    original_cv: str,
    fixed_cv: str,
    detected_issues: Optional[List[Dict]] = None
) -> Dict:
    """
    Generate a structured changes report by comparing original and fixed CV.
    
    Args:
        original_cv: The original CV text before fixes
        fixed_cv: The CV text after AI-based Auto-Fix
        detected_issues: List of issues that were detected (for context)
    
    Returns:
        Dict matching the expected JSON format:
        {
            "changes": [...],
            "summary": {
                "total_changes": int,
                "by_category": {...}
            }
        }
    """
    changes = []
    
    line_changes = _extract_line_changes(original_cv, fixed_cv)
    changes.extend(line_changes)
    
    if detected_issues:
        changes = _enrich_with_issue_context(changes, detected_issues)
    
    structural_changes = _detect_structural_changes(original_cv, fixed_cv)
    changes.extend(structural_changes)
    
    changes = _deduplicate_changes(changes)
    
    summary = _build_summary(changes)
    
    return {
        "changes": changes,
        "summary": summary
    }


def _extract_line_changes(original: str, fixed: str) -> List[Dict]:
    """
    Extract changes using line-by-line comparison.
    """
    changes = []
    
    original_lines = original.strip().split('\n')
    fixed_lines = fixed.strip().split('\n')
    
    matcher = SequenceMatcher(None, original_lines, fixed_lines)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            original_text = '\n'.join(original_lines[i1:i2]).strip()
            fixed_text = '\n'.join(fixed_lines[j1:j2]).strip()
            
            if original_text and fixed_text and original_text != fixed_text:
                category = _categorize_change(original_text, fixed_text)
                explanation = _generate_explanation(category, original_text, fixed_text)
                
                changes.append({
                    "category": category,
                    "before": _truncate(original_text, 200),
                    "after": _truncate(fixed_text, 200),
                    "explanation": explanation
                })
                
        elif tag == 'insert':
            added_text = '\n'.join(fixed_lines[j1:j2]).strip()
            if added_text:
                category = _categorize_addition(added_text)
                changes.append({
                    "category": category,
                    "before": "",
                    "after": _truncate(added_text, 200),
                    "explanation": f"Added new content"
                })
                
        elif tag == 'delete':
            deleted_text = '\n'.join(original_lines[i1:i2]).strip()
            if deleted_text and len(deleted_text) > 10:
                changes.append({
                    "category": "other",
                    "before": _truncate(deleted_text, 200),
                    "after": "",
                    "explanation": "Removed redundant content"
                })
    
    return changes


def _categorize_change(before: str, after: str) -> str:
    """
    Categorize a change based on what was modified.
    Categories: quantification, language, grammar, formatting, other
    """
    before_lower = before.lower()
    after_lower = after.lower()
    
    before_numbers = len(re.findall(r'\b\d+[%$KMB]?\b', before))
    after_numbers = len(re.findall(r'\b\d+[%$KMB]?\b', after))
    if after_numbers > before_numbers:
        return "quantification"
    
    weak_words = ['responsible for', 'helped', 'assisted', 'worked on', 'was involved']
    strong_verbs = ['led', 'managed', 'developed', 'created', 'implemented', 'achieved', 
                    'increased', 'decreased', 'improved', 'launched', 'delivered']
    
    had_weak = any(w in before_lower for w in weak_words)
    has_strong = any(v in after_lower for v in strong_verbs)
    if had_weak or has_strong:
        return "language"
    
    grammar_patterns = [
        (r'\bi\b', r'\b(I)\b'),
        (r'\.{2,}', r'\.'),
        (r'\s{2,}', r'\s'),
    ]
    for pattern_before, pattern_after in grammar_patterns:
        if re.search(pattern_before, before) and not re.search(pattern_before, after):
            return "grammar"
    
    if _is_formatting_change(before, after):
        return "formatting"
    
    return "other"


def _is_formatting_change(before: str, after: str) -> bool:
    """
    Check if the change is primarily formatting-related.
    """
    date_patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b',
        r'\b\d{4}\s*[-–]\s*(Present|Current|\d{4})\b'
    ]
    
    for pattern in date_patterns:
        before_dates = len(re.findall(pattern, before, re.IGNORECASE))
        after_dates = len(re.findall(pattern, after, re.IGNORECASE))
        if before_dates != after_dates or (before_dates > 0 and after_dates > 0):
            return True
    
    before_bullets = len(re.findall(r'^[\s]*[-•●○►]\s', before, re.MULTILINE))
    after_bullets = len(re.findall(r'^[\s]*[-•●○►]\s', after, re.MULTILINE))
    if before_bullets != after_bullets:
        return True
    
    return False


def _categorize_addition(text: str) -> str:
    """
    Categorize newly added content.
    """
    text_lower = text.lower()
    
    section_keywords = ['summary', 'objective', 'skills', 'experience', 'education',
                       'certifications', 'projects', 'awards', 'languages']
    if any(kw in text_lower for kw in section_keywords):
        return "formatting"
    
    if re.search(r'\b\d+[%$KMB]?\b', text):
        return "quantification"
    
    return "other"


def _generate_explanation(category: str, before: str, after: str) -> str:
    """
    Generate a human-readable explanation for the change.
    """
    explanations = {
        "quantification": "Added specific metrics to strengthen achievement",
        "language": "Improved language with stronger action verbs",
        "grammar": "Fixed grammar or spelling",
        "formatting": "Improved formatting and structure",
        "other": "Enhanced content clarity"
    }
    
    before_lower = before.lower()
    after_lower = after.lower()
    
    if category == "quantification":
        numbers = re.findall(r'\b(\d+[%$KMB]?)\b', after)
        if numbers:
            return f"Added quantified results ({', '.join(numbers[:3])})"
    
    if category == "language":
        weak_found = None
        for weak in ['responsible for', 'helped', 'assisted', 'worked on']:
            if weak in before_lower and weak not in after_lower:
                weak_found = weak
                break
        if weak_found:
            return f"Replaced '{weak_found}' with stronger action verb"
    
    return explanations.get(category, "Improved content")


def _detect_structural_changes(original: str, fixed: str) -> List[Dict]:
    """
    Detect high-level structural changes (sections added/improved).
    """
    changes = []
    
    sections = {
        'summary': ['summary', 'professional summary', 'profile'],
        'skills': ['skills', 'technical skills', 'core competencies'],
        'education': ['education', 'academic'],
        'certifications': ['certification', 'certificates'],
    }
    
    for section_name, keywords in sections.items():
        original_has = any(kw in original.lower() for kw in keywords)
        fixed_has = any(kw in fixed.lower() for kw in keywords)
        
        if not original_has and fixed_has:
            changes.append({
                "category": "formatting",
                "before": "",
                "after": f"[{section_name.title()} section]",
                "explanation": f"Added {section_name} section"
            })
    
    return changes


def _enrich_with_issue_context(changes: List[Dict], detected_issues: List[Dict]) -> List[Dict]:
    """
    Use detected issues to improve change explanations.
    """
    issue_explanations = {}
    for issue in detected_issues:
        issue_type = issue.get('issue_type', issue.get('type', ''))
        suggested_fix = issue.get('suggested_fix', issue.get('fix', ''))
        if issue_type and suggested_fix:
            issue_explanations[issue_type.lower()] = suggested_fix
    
    for change in changes:
        change_text = (change.get('before', '') + change.get('after', '')).lower()
        
        for issue_type, fix_text in issue_explanations.items():
            if issue_type in change_text or any(word in change_text for word in issue_type.split('_')):
                change['explanation'] = _truncate(fix_text, 100)
                break
    
    return changes


def _deduplicate_changes(changes: List[Dict]) -> List[Dict]:
    """
    Remove duplicate or overlapping changes.
    """
    seen_befores = set()
    unique = []
    
    for change in changes:
        before_key = change.get('before', '')[:50]
        if before_key not in seen_befores or not before_key:
            seen_befores.add(before_key)
            unique.append(change)
    
    return unique


def _build_summary(changes: List[Dict]) -> Dict:
    """
    Build summary statistics matching expected format.
    """
    by_category = {
        "quantification": 0,
        "language": 0,
        "grammar": 0,
        "formatting": 0,
        "other": 0
    }
    
    for change in changes:
        cat = change.get('category', 'other')
        if cat in by_category:
            by_category[cat] += 1
        else:
            by_category['other'] += 1
    
    return {
        "total_changes": len(changes),
        "by_category": by_category
    }


def _truncate(text: str, max_length: int) -> str:
    """
    Truncate text to max length with ellipsis.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
