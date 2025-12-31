"""
Scoring Configuration - Weights and Thresholds
Version: 4.0

CRITICAL: These values are the SINGLE SOURCE OF TRUTH for scoring.
Do NOT modify without updating documentation.
"""

# Score bounds
SCORE_MIN = 10
SCORE_MAX = 95

# Category weights (MUST sum to 100)
CATEGORY_WEIGHTS = {
    'content_quality': 40,      # Quantification, Action Verbs, Narrative, Depth
    'language_clarity': 18,     # Grammar, Writing Quality, Vagueness
    'formatting': 18,           # Visual Structure, Organization, Consistency, ATS
    'completeness': 12,         # Contact, Required Sections, Keywords, Job Standards
    'professional': 8,          # Length, Recency, Certifications
    'red_flags': 4              # Repetition, Critical Issues
}

# Verify weights sum to 100
assert sum(CATEGORY_WEIGHTS.values()) == 100, "Category weights must sum to 100"

# Grade thresholds
GRADE_THRESHOLDS = {
    'excellent': 90,
    'good': 75,
    'fair': 60,
    'needs_work': 45,
    'poor': 0
}

# Sub-category weights within Content Quality (40 points)
CONTENT_QUALITY_WEIGHTS = {
    'quantification': 20,       # QNT-001 to QNT-007
    'action_verbs': 8,          # AVB-001 to AVB-004
    'career_narrative': 6,      # NAR-001 to NAR-004
    'content_depth': 6          # DEP-001 to DEP-006
}

# Sub-category weights within Language & Clarity (18 points)
LANGUAGE_CLARITY_WEIGHTS = {
    'grammar_spelling': 8,      # GRM-001 to GRM-005
    'writing_quality': 5,       # WRT-001 to WRT-006
    'vagueness': 5              # VAG-001 to VAG-005
}

# Sub-category weights within Formatting (18 points)
FORMATTING_WEIGHTS = {
    'visual_structure': 6,      # FMT-001 to FMT-004
    'section_organization': 5,  # SEC-001 to SEC-004
    'consistency': 3,           # CON-001 to CON-003
    'ats_compatibility': 4      # ATS-001 to ATS-010
}

# Sub-category weights within Completeness (12 points)
COMPLETENESS_WEIGHTS = {
    'contact_info': 4,          # CNT-001 to CNT-005
    'required_sections': 3,     # REQ-001 to REQ-003
    'keywords_skills': 2,       # KEY-001 to KEY-003
    'job_entry_standards': 3    # JOB-001 to JOB-008
}

# Sub-category weights within Professional Standards (8 points)
PROFESSIONAL_WEIGHTS = {
    'length': 2,                # LEN-001 to LEN-003
    'recency_relevance': 3,     # REC-001 to REC-007
    'certifications': 3         # CRT-001 to CRT-005
}

# Sub-category weights within Red Flags (4 points)
RED_FLAGS_WEIGHTS = {
    'repetition': 2,            # REP-001 to REP-005
    'critical_flags': 2         # RED-001 to RED-008
}

# Fixability rates (for after-fix score projection)
FIXABILITY_RATES = {
    'grammar': 0.95,
    'spelling': 0.95,
    'action_verbs': 0.85,
    'formatting': 0.70,
    'language': 0.80,
    'quantification': 0.40,
    'contact': 0.10,
    'gaps': 0.00
}

# Strong action verbs list
STRONG_VERBS = [
    'Led', 'Directed', 'Managed', 'Supervised', 'Headed', 'Oversaw',
    'Coordinated', 'Orchestrated', 'Spearheaded', 'Championed',
    'Achieved', 'Accomplished', 'Attained', 'Exceeded', 'Surpassed',
    'Outperformed', 'Delivered', 'Completed',
    'Created', 'Developed', 'Designed', 'Built', 'Established',
    'Founded', 'Initiated', 'Launched', 'Pioneered', 'Introduced',
    'Improved', 'Enhanced', 'Optimized', 'Streamlined', 'Transformed',
    'Revitalized', 'Modernized', 'Upgraded', 'Refined',
    'Increased', 'Expanded', 'Grew', 'Scaled', 'Accelerated',
    'Amplified', 'Boosted', 'Maximized',
    'Analyzed', 'Assessed', 'Evaluated', 'Researched', 'Investigated',
    'Examined', 'Audited', 'Diagnosed',
    'Presented', 'Negotiated', 'Persuaded', 'Influenced', 'Advocated',
    'Articulated', 'Communicated',
    'Engineered', 'Programmed', 'Architected', 'Implemented',
    'Integrated', 'Automated', 'Configured', 'Deployed'
]

# Weak verbs list
WEAK_VERBS = [
    'Helped', 'Assisted', 'Supported', 'Worked on', 'Was responsible for',
    'Participated in', 'Contributed to', 'Involved in', 'Handled',
    'Dealt with', 'Did', 'Made', 'Got', 'Tried to', 'Was part of'
]

# Redundant phrases to detect
REDUNDANT_PHRASES = [
    'in order to',
    'due to the fact that',
    'at this point in time',
    'for the purpose of',
    'in the event that',
    'a total of',
    'each and every'
]

# Filler words to detect
FILLER_WORDS = [
    'very', 'really', 'basically', 'actually',
    'just', 'quite', 'somewhat', 'rather'
]

# Vague phrases to flag
VAGUE_PHRASES = [
    'various', 'multiple', 'numerous', 'several',
    'significant', 'substantial', 'considerable',
    'helped improve', 'assisted with', 'was involved in',
    'played a role', 'contributed to success'
]

# ═══════════════════════════════════════════════════════════════════
# ISSUE TYPE CONFIGURATION - SINGLE SOURCE OF TRUTH
# ═══════════════════════════════════════════════════════════════════
# 
# SEVERITY LEVELS:
#   critical → "Quick Wins" in UI (red badge) - Immediate rejection risk
#   high     → "Important" in UI (orange badge) - Major disadvantage
#   medium   → "Consider" in UI (yellow badge) - Optimization opportunity
#   low      → "Polish" in UI (green badge) - Minor improvements
#
# DO NOT let AI assign severity - use this config instead!
# ═══════════════════════════════════════════════════════════════════

ISSUE_TYPE_CONFIG = {
    # ─────────────────────────────────────────────────────────────────
    # CRITICAL - Immediate rejection risk
    # ─────────────────────────────────────────────────────────────────
    'SPELLING_ERROR': {
        'severity': 'critical',
        'ui_category': 'spelling_grammar',
        'display_name': 'Spelling Error',
        'auto_fixable': True,
    },
    'GRAMMAR_ERROR': {
        'severity': 'critical',
        'ui_category': 'spelling_grammar',
        'display_name': 'Grammar Error',
        'auto_fixable': True,
    },
    'MISSING_EMAIL': {
        'severity': 'critical',
        'ui_category': 'contact_information',
        'display_name': 'Missing Email',
        'auto_fixable': False,
    },
    'MISSING_PHONE': {
        'severity': 'critical',
        'ui_category': 'contact_information',
        'display_name': 'Missing Phone',
        'auto_fixable': False,
    },
    'INVALID_EMAIL': {
        'severity': 'critical',
        'ui_category': 'contact_information',
        'display_name': 'Invalid Email Format',
        'auto_fixable': False,
    },
    'INVALID_PHONE': {
        'severity': 'critical',
        'ui_category': 'contact_information',
        'display_name': 'Invalid Phone Format',
        'auto_fixable': False,
    },
    
    # ─────────────────────────────────────────────────────────────────
    # HIGH - Major competitive disadvantage
    # ─────────────────────────────────────────────────────────────────
    'NO_METRICS': {
        'severity': 'high',
        'ui_category': 'quantified_achievements',
        'display_name': 'No Quantified Achievement',
        'auto_fixable': False,
    },
    'WEAK_ACTION_VERBS': {
        'severity': 'high',
        'ui_category': 'action_verbs',
        'display_name': 'Weak Action Verb',
        'auto_fixable': True,
    },
    'EMPLOYMENT_GAP': {
        'severity': 'high',
        'ui_category': 'career_gaps',
        'display_name': 'Employment Gap',
        'auto_fixable': False,
    },
    'MISSING_LINKEDIN': {
        'severity': 'high',
        'ui_category': 'contact_information',
        'display_name': 'Missing LinkedIn',
        'auto_fixable': False,
    },
    'VAGUE_DESCRIPTION': {
        'severity': 'high',
        'ui_category': 'career_narrative',
        'display_name': 'Vague Description',
        'auto_fixable': True,
    },
    'NO_ACHIEVEMENTS': {
        'severity': 'high',
        'ui_category': 'quantified_achievements',
        'display_name': 'No Achievements Listed',
        'auto_fixable': False,
    },
    'MISSING_DATES': {
        'severity': 'high',
        'ui_category': 'career_gaps',
        'display_name': 'Missing Dates',
        'auto_fixable': False,
    },
    'MISSING_COMPANY': {
        'severity': 'high',
        'ui_category': 'career_narrative',
        'display_name': 'Missing Company Name',
        'auto_fixable': False,
    },
    'MISSING_TITLE': {
        'severity': 'high',
        'ui_category': 'career_narrative',
        'display_name': 'Missing Job Title',
        'auto_fixable': False,
    },
    'BUZZWORD_STUFFING': {
        'severity': 'high',
        'ui_category': 'career_narrative',
        'display_name': 'Buzzword Overuse',
        'auto_fixable': True,
    },
    
    # ─────────────────────────────────────────────────────────────────
    # MEDIUM - Optimization opportunities
    # ─────────────────────────────────────────────────────────────────
    'FORMAT_INCONSISTENT': {
        'severity': 'medium',
        'ui_category': 'professional_formatting',
        'display_name': 'Inconsistent Formatting',
        'auto_fixable': True,
    },
    'WEAK_SUMMARY': {
        'severity': 'medium',
        'ui_category': 'career_narrative',
        'display_name': 'Weak Summary',
        'auto_fixable': True,
    },
    'SECTION_ORDER': {
        'severity': 'medium',
        'ui_category': 'cv_length_structure',
        'display_name': 'Suboptimal Section Order',
        'auto_fixable': True,
    },
    'ATS_INCOMPATIBLE': {
        'severity': 'medium',
        'ui_category': 'professional_formatting',
        'display_name': 'ATS Compatibility Issue',
        'auto_fixable': True,
    },
    'BULLET_FORMAT': {
        'severity': 'medium',
        'ui_category': 'professional_formatting',
        'display_name': 'Bullet Point Format',
        'auto_fixable': True,
    },
    'MISSING_KEYWORDS': {
        'severity': 'medium',
        'ui_category': 'keywords_skills',
        'display_name': 'Missing Keywords',
        'auto_fixable': False,
    },
    'DATE_FORMAT_INCONSISTENT': {
        'severity': 'medium',
        'ui_category': 'professional_formatting',
        'display_name': 'Inconsistent Date Format',
        'auto_fixable': True,
    },
    'CONTACT_INCOMPLETE': {
        'severity': 'medium',
        'ui_category': 'contact_information',
        'display_name': 'Incomplete Contact Info',
        'auto_fixable': False,
    },
    'SKILLS_UNORGANIZED': {
        'severity': 'medium',
        'ui_category': 'keywords_skills',
        'display_name': 'Unorganized Skills',
        'auto_fixable': True,
    },
    'REPETITIVE_CONTENT': {
        'severity': 'medium',
        'ui_category': 'career_narrative',
        'display_name': 'Repetitive Content',
        'auto_fixable': True,
    },
    
    # ─────────────────────────────────────────────────────────────────
    # LOW - Minor polish
    # ─────────────────────────────────────────────────────────────────
    'CV_TOO_LONG': {
        'severity': 'low',
        'ui_category': 'cv_length_structure',
        'display_name': 'CV Too Long',
        'auto_fixable': False,
    },
    'CV_TOO_SHORT': {
        'severity': 'low',
        'ui_category': 'cv_length_structure',
        'display_name': 'CV Too Short',
        'auto_fixable': False,
    },
    'BULLET_TOO_LONG': {
        'severity': 'low',
        'ui_category': 'professional_formatting',
        'display_name': 'Bullet Too Long',
        'auto_fixable': True,
    },
    'BULLET_TOO_SHORT': {
        'severity': 'low',
        'ui_category': 'professional_formatting',
        'display_name': 'Bullet Too Short',
        'auto_fixable': False,
    },
    'WHITESPACE_ISSUE': {
        'severity': 'low',
        'ui_category': 'professional_formatting',
        'display_name': 'Whitespace Issue',
        'auto_fixable': True,
    },
    'MINOR_FORMAT': {
        'severity': 'low',
        'ui_category': 'professional_formatting',
        'display_name': 'Minor Format Issue',
        'auto_fixable': True,
    },
    'HEADER_STYLE': {
        'severity': 'low',
        'ui_category': 'professional_formatting',
        'display_name': 'Header Style',
        'auto_fixable': True,
    },
    'OUTDATED_INFO': {
        'severity': 'low',
        'ui_category': 'career_narrative',
        'display_name': 'Outdated Information',
        'auto_fixable': False,
    },
}

# Default severity for unknown issue types (fallback)
DEFAULT_SEVERITY = 'medium'
DEFAULT_UI_CATEGORY = 'career_narrative'

# Valid severity levels (for validation)
VALID_SEVERITIES = ['critical', 'high', 'medium', 'low']

# Issue type enum list (for AI prompt reference)
ISSUE_TYPE_ENUM = list(ISSUE_TYPE_CONFIG.keys())
