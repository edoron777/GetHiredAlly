"""
CV Bullet Point Extractor

Extracts and analyzes individual bullet points/achievements.
100% CODE - No AI - Deterministic results.
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class BulletPoint:
    """A single bullet point from CV."""
    text: str
    line_number: int
    word_count: int
    has_metrics: bool
    has_strong_verb: bool
    starts_with_verb: bool
    metrics_found: List[str]


BULLET_MARKERS = re.compile(r'^[\s]*[•\-\*\>\◦\▪\●\○][\s]+', re.MULTILINE)

METRICS_PATTERNS = [
    re.compile(r'\d+%'),
    re.compile(r'\$[\d,]+(?:\.\d{2})?[KMB]?'),
    re.compile(r'[\d,]+\+?(?:\s+)(?:users?|customers?|clients?|employees?|people|members?|subscribers?|visitors?)', re.IGNORECASE),
    re.compile(r'(?:increased?|decreased?|reduced?|improved?|grew?|raised?|cut|saved?)\s+(?:by\s+)?\d+', re.IGNORECASE),
    re.compile(r'\d+x\b'),
    re.compile(r'#\d+\b'),
    re.compile(r'\b\d{1,3}(?:,\d{3})+\b'),
]

STRONG_VERB_STARTS = [
    'achieved', 'accomplished', 'accelerated', 'acquired', 'advanced',
    'built', 'boosted',
    'created', 'championed', 'consolidated', 'coordinated',
    'delivered', 'designed', 'developed', 'directed', 'drove',
    'earned', 'eliminated', 'enhanced', 'established', 'exceeded', 'expanded',
    'facilitated', 'founded',
    'generated', 'grew', 'guided',
    'headed',
    'identified', 'implemented', 'improved', 'increased', 'initiated', 'introduced',
    'launched', 'led',
    'managed', 'maximized', 'mentored', 'modernized',
    'negotiated',
    'optimized', 'orchestrated', 'organized', 'oversaw',
    'partnered', 'pioneered', 'planned', 'presented', 'produced', 'programmed',
    'raised', 'reduced', 'redesigned', 'reorganized', 'resolved', 'restructured', 'revamped',
    'saved', 'scaled', 'secured', 'simplified', 'spearheaded', 'standardized', 'streamlined', 'strengthened', 'supervised',
    'trained', 'transformed',
    'unified', 'upgraded',
    'won',
]


def extract_bullets(text: str) -> List[BulletPoint]:
    """
    Extract all bullet points from text.
    
    Args:
        text: CV text (or section text)
        
    Returns:
        List of BulletPoint objects
    """
    bullets = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        is_bullet = False
        clean_line = line
        
        if BULLET_MARKERS.match(line):
            is_bullet = True
            clean_line = BULLET_MARKERS.sub('', line).strip()
        elif line and line[0].isupper():
            first_word = line.split()[0].lower().rstrip('ed').rstrip('ing') if line.split() else ''
            for verb in STRONG_VERB_STARTS:
                if first_word == verb or first_word == verb.rstrip('ed') or line.lower().startswith(verb):
                    is_bullet = True
                    clean_line = line
                    break
        
        if is_bullet and len(clean_line) > 10:
            bullet = analyze_bullet(clean_line, i + 1)
            bullets.append(bullet)
    
    return bullets


def analyze_bullet(text: str, line_number: int) -> BulletPoint:
    """
    Analyze a single bullet point.
    
    Args:
        text: The bullet text
        line_number: Line number in original document
        
    Returns:
        BulletPoint with analysis
    """
    metrics_found = []
    for pattern in METRICS_PATTERNS:
        matches = pattern.findall(text)
        metrics_found.extend(matches)
    
    words = text.split()
    first_word = words[0].lower().rstrip(',.:;') if words else ''
    
    starts_with_verb = any(
        first_word == verb or first_word.startswith(verb.rstrip('ed'))
        for verb in STRONG_VERB_STARTS
    )
    
    text_lower = text.lower()
    has_strong_verb = any(verb in text_lower for verb in STRONG_VERB_STARTS)
    
    return BulletPoint(
        text=text,
        line_number=line_number,
        word_count=len(words),
        has_metrics=len(metrics_found) > 0,
        has_strong_verb=has_strong_verb,
        starts_with_verb=starts_with_verb,
        metrics_found=metrics_found,
    )


MAX_ISSUES_PER_TYPE = 5


def get_bullet_issues(bullets: List[BulletPoint], max_per_type: int = MAX_ISSUES_PER_TYPE) -> List[Dict]:
    """
    Generate issues based on bullet analysis.
    
    Limits issues per type to avoid overwhelming users (e.g., max 5 "missing metrics" issues).
    
    Args:
        bullets: List of extracted BulletPoint objects
        max_per_type: Maximum issues to generate per issue type (default 5)
        
    Returns:
        List of issue dictionaries with issue_type
    """
    issues = []
    
    missing_metrics_count = 0
    weak_verbs_count = 0
    too_long_count = 0
    too_short_count = 0
    
    for bullet in bullets:
        if not bullet.has_metrics and missing_metrics_count < max_per_type:
            issues.append({
                'issue_type': 'CONTENT_MISSING_METRICS',
                'location': f'Line {bullet.line_number}',
                'description': 'Bullet point lacks quantified achievement (no numbers, percentages, or metrics)',
                'current': bullet.text[:100] + '...' if len(bullet.text) > 100 else bullet.text,
            })
            missing_metrics_count += 1
        
        if not bullet.starts_with_verb and weak_verbs_count < max_per_type:
            issues.append({
                'issue_type': 'CONTENT_WEAK_ACTION_VERBS',
                'location': f'Line {bullet.line_number}',
                'description': 'Bullet should start with a strong action verb',
                'current': bullet.text[:50] + '...' if len(bullet.text) > 50 else bullet.text,
            })
            weak_verbs_count += 1
        
        if bullet.word_count > 30 and too_long_count < max_per_type:
            issues.append({
                'issue_type': 'CONTENT_BULLET_TOO_LONG',
                'location': f'Line {bullet.line_number}',
                'description': f'Bullet is {bullet.word_count} words - consider splitting or condensing',
                'current': bullet.text[:100] + '...',
            })
            too_long_count += 1
        
        if bullet.word_count < 5 and too_short_count < max_per_type:
            issues.append({
                'issue_type': 'CONTENT_BULLET_TOO_SHORT',
                'location': f'Line {bullet.line_number}',
                'description': f'Bullet is only {bullet.word_count} words - add more detail',
                'current': bullet.text,
            })
            too_short_count += 1
    
    return issues
