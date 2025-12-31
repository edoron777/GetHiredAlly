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
# DEPRECATED: ISSUE_TYPE_CONFIG
# 
# This config has been moved to the database (cv_issue_types table).
# The CatalogService now provides all issue type metadata.
# 
# Kept here for backward compatibility with existing code that may
# still reference ISSUE_TYPE_CONFIG or ISSUE_TYPE_ENUM.
# New code should use: from common.catalog import get_catalog_service
# 
# Date deprecated: 2025-12-31
# ═══════════════════════════════════════════════════════════════════

ISSUE_TYPE_CONFIG = {
    # ─────────────────────────────────────────────────────────────────
    # CATEGORY 1: CONTACT INFORMATION (8 types)
    # ─────────────────────────────────────────────────────────────────
    'CONTACT_MISSING_EMAIL': {
        'severity': 'critical',
        'weight': 10,
        'category': 'Contact Information',
        'subcategory': 'Missing Information',
        'auto_fixable': False,
        'display_name': 'Missing Email Address',
        'detection_method': 'regex'
    },
    'CONTACT_MISSING_PHONE': {
        'severity': 'critical',
        'weight': 9,
        'category': 'Contact Information',
        'subcategory': 'Missing Information',
        'auto_fixable': False,
        'display_name': 'Missing Phone Number',
        'detection_method': 'regex'
    },
    'CONTACT_MISSING_LINKEDIN': {
        'severity': 'important',
        'weight': 7,
        'category': 'Contact Information',
        'subcategory': 'Missing Information',
        'auto_fixable': False,
        'display_name': 'No LinkedIn Profile URL',
        'detection_method': 'regex'
    },
    'CONTACT_MISSING_LOCATION': {
        'severity': 'important',
        'weight': 6,
        'category': 'Contact Information',
        'subcategory': 'Missing Information',
        'auto_fixable': False,
        'display_name': 'Missing Location/City',
        'detection_method': 'regex'
    },
    'CONTACT_UNPROFESSIONAL_EMAIL': {
        'severity': 'important',
        'weight': 7,
        'category': 'Contact Information',
        'subcategory': 'Format Issues',
        'auto_fixable': False,
        'display_name': 'Unprofessional Email Address',
        'detection_method': 'regex'
    },
    'CONTACT_INCONSISTENT_FORMAT': {
        'severity': 'consider',
        'weight': 3,
        'category': 'Contact Information',
        'subcategory': 'Format Issues',
        'auto_fixable': True,
        'display_name': 'Inconsistent Contact Format',
        'detection_method': 'regex'
    },
    'CONTACT_PHOTO_INCLUDED': {
        'severity': 'important',
        'weight': 6,
        'category': 'Contact Information',
        'subcategory': 'Professional Standards',
        'auto_fixable': True,
        'display_name': 'Photo Included on CV',
        'detection_method': 'rule'
    },
    'CONTACT_PERSONAL_INFO_EXCESSIVE': {
        'severity': 'important',
        'weight': 5,
        'category': 'Contact Information',
        'subcategory': 'Professional Standards',
        'auto_fixable': True,
        'display_name': 'Excessive Personal Information',
        'detection_method': 'regex'
    },
    
    # ─────────────────────────────────────────────────────────────────
    # CATEGORY 2: FORMATTING & STRUCTURE (13 types)
    # ─────────────────────────────────────────────────────────────────
    'FORMAT_INCONSISTENT_DATES': {
        'severity': 'consider',
        'weight': 4,
        'category': 'Formatting & Structure',
        'subcategory': 'Consistency Issues',
        'auto_fixable': True,
        'display_name': 'Inconsistent Date Formats',
        'detection_method': 'regex'
    },
    'FORMAT_INCONSISTENT_BULLETS': {
        'severity': 'consider',
        'weight': 3,
        'category': 'Formatting & Structure',
        'subcategory': 'Consistency Issues',
        'auto_fixable': True,
        'display_name': 'Inconsistent Bullet Point Styles',
        'detection_method': 'regex'
    },
    'FORMAT_INCONSISTENT_CAPITALIZATION': {
        'severity': 'consider',
        'weight': 3,
        'category': 'Formatting & Structure',
        'subcategory': 'Consistency Issues',
        'auto_fixable': True,
        'display_name': 'Inconsistent Header Capitalization',
        'detection_method': 'regex'
    },
    'FORMAT_INCONSISTENT_SPACING': {
        'severity': 'polish',
        'weight': 2,
        'category': 'Formatting & Structure',
        'subcategory': 'Consistency Issues',
        'auto_fixable': True,
        'display_name': 'Inconsistent Spacing',
        'detection_method': 'rule'
    },
    'FORMAT_MISSING_SECTION_HEADERS': {
        'severity': 'critical',
        'weight': 8,
        'category': 'Formatting & Structure',
        'subcategory': 'Visual Hierarchy',
        'auto_fixable': False,
        'display_name': 'Missing Section Headers',
        'detection_method': 'nlp'
    },
    'FORMAT_POOR_VISUAL_HIERARCHY': {
        'severity': 'important',
        'weight': 6,
        'category': 'Formatting & Structure',
        'subcategory': 'Visual Hierarchy',
        'auto_fixable': False,
        'display_name': 'Poor Visual Hierarchy',
        'detection_method': 'rule'
    },
    'FORMAT_TRAILING_WHITESPACE': {
        'severity': 'polish',
        'weight': 1,
        'category': 'Formatting & Structure',
        'subcategory': 'Whitespace & Spacing',
        'auto_fixable': True,
        'display_name': 'Trailing Whitespace',
        'detection_method': 'regex'
    },
    'FORMAT_MULTIPLE_SPACES': {
        'severity': 'polish',
        'weight': 1,
        'category': 'Formatting & Structure',
        'subcategory': 'Whitespace & Spacing',
        'auto_fixable': True,
        'display_name': 'Multiple Consecutive Spaces',
        'detection_method': 'regex'
    },
    'FORMAT_EXCESSIVE_BLANK_LINES': {
        'severity': 'consider',
        'weight': 2,
        'category': 'Formatting & Structure',
        'subcategory': 'Whitespace & Spacing',
        'auto_fixable': True,
        'display_name': 'Excessive Blank Lines',
        'detection_method': 'regex'
    },
    'FORMAT_TABLES_DETECTED': {
        'severity': 'important',
        'weight': 7,
        'category': 'Formatting & Structure',
        'subcategory': 'ATS Compatibility',
        'auto_fixable': False,
        'display_name': 'Tables May Cause ATS Issues',
        'detection_method': 'rule'
    },
    'FORMAT_MULTIPLE_COLUMNS': {
        'severity': 'important',
        'weight': 7,
        'category': 'Formatting & Structure',
        'subcategory': 'ATS Compatibility',
        'auto_fixable': False,
        'display_name': 'Multiple Columns May Cause ATS Issues',
        'detection_method': 'rule'
    },
    'FORMAT_SPECIAL_CHARACTERS': {
        'severity': 'consider',
        'weight': 4,
        'category': 'Formatting & Structure',
        'subcategory': 'ATS Compatibility',
        'auto_fixable': True,
        'display_name': 'Special Characters May Not Display',
        'detection_method': 'regex'
    },
    'FORMAT_HEADERS_GRAPHICS': {
        'severity': 'critical',
        'weight': 9,
        'category': 'Formatting & Structure',
        'subcategory': 'ATS Compatibility',
        'auto_fixable': False,
        'display_name': 'Header Contains Graphics',
        'detection_method': 'rule'
    },
    
    # ─────────────────────────────────────────────────────────────────
    # CATEGORY 3: CONTENT QUALITY (12 types)
    # ─────────────────────────────────────────────────────────────────
    'CONTENT_TASK_FOCUSED': {
        'severity': 'critical',
        'weight': 10,
        'category': 'Content Quality',
        'subcategory': 'Achievement vs Task Focus',
        'auto_fixable': False,
        'display_name': 'Task-Focused Instead of Achievement-Focused',
        'detection_method': 'nlp'
    },
    'CONTENT_MISSING_IMPACT': {
        'severity': 'important',
        'weight': 8,
        'category': 'Content Quality',
        'subcategory': 'Achievement vs Task Focus',
        'auto_fixable': False,
        'display_name': 'Missing Impact/Results',
        'detection_method': 'nlp'
    },
    'CONTENT_MISSING_METRICS': {
        'severity': 'critical',
        'weight': 10,
        'category': 'Content Quality',
        'subcategory': 'Quantification & Metrics',
        'auto_fixable': False,
        'display_name': 'Missing Quantifiable Metrics',
        'detection_method': 'nlp'
    },
    'CONTENT_VAGUE_METRICS': {
        'severity': 'important',
        'weight': 6,
        'category': 'Content Quality',
        'subcategory': 'Quantification & Metrics',
        'auto_fixable': False,
        'display_name': 'Vague or Weak Metrics',
        'detection_method': 'nlp'
    },
    'CONTENT_WEAK_ACTION_VERBS': {
        'severity': 'important',
        'weight': 6,
        'category': 'Content Quality',
        'subcategory': 'Action Verbs & Language',
        'auto_fixable': True,
        'display_name': 'Weak or Passive Action Verbs',
        'detection_method': 'nlp'
    },
    'CONTENT_FIRST_PERSON_PRONOUNS': {
        'severity': 'consider',
        'weight': 3,
        'category': 'Content Quality',
        'subcategory': 'Action Verbs & Language',
        'auto_fixable': True,
        'display_name': 'First Person Pronouns (I, Me, My)',
        'detection_method': 'regex'
    },
    'CONTENT_PASSIVE_VOICE': {
        'severity': 'consider',
        'weight': 4,
        'category': 'Content Quality',
        'subcategory': 'Action Verbs & Language',
        'auto_fixable': True,
        'display_name': 'Passive Voice Usage',
        'detection_method': 'nlp'
    },
    'CONTENT_IRRELEVANT_INFORMATION': {
        'severity': 'consider',
        'weight': 5,
        'category': 'Content Quality',
        'subcategory': 'Relevance & Focus',
        'auto_fixable': False,
        'display_name': 'Irrelevant Information Included',
        'detection_method': 'nlp'
    },
    'CONTENT_GENERIC_STATEMENTS': {
        'severity': 'important',
        'weight': 6,
        'category': 'Content Quality',
        'subcategory': 'Relevance & Focus',
        'auto_fixable': False,
        'display_name': 'Generic/Cliché Statements',
        'detection_method': 'nlp'
    },
    'CONTENT_BULLET_TOO_SHORT': {
        'severity': 'important',
        'weight': 6,
        'category': 'Content Quality',
        'subcategory': 'Bullet Point Quality',
        'auto_fixable': False,
        'display_name': 'Bullet Point Too Short',
        'detection_method': 'rule'
    },
    'CONTENT_BULLET_TOO_LONG': {
        'severity': 'consider',
        'weight': 4,
        'category': 'Content Quality',
        'subcategory': 'Bullet Point Quality',
        'auto_fixable': False,
        'display_name': 'Bullet Point Too Long',
        'detection_method': 'rule'
    },
    'CONTENT_TOO_MANY_BULLETS': {
        'severity': 'consider',
        'weight': 4,
        'category': 'Content Quality',
        'subcategory': 'Bullet Point Quality',
        'auto_fixable': False,
        'display_name': 'Too Many Bullets Per Role',
        'detection_method': 'rule'
    },
    
    # ─────────────────────────────────────────────────────────────────
    # CATEGORY 4: GRAMMAR & LANGUAGE (7 types)
    # ─────────────────────────────────────────────────────────────────
    'GRAMMAR_SPELLING_ERROR': {
        'severity': 'critical',
        'weight': 9,
        'category': 'Grammar & Language',
        'subcategory': 'Spelling',
        'auto_fixable': True,
        'display_name': 'Spelling Error',
        'detection_method': 'nlp'
    },
    'GRAMMAR_COMPANY_NAME_SPELLING': {
        'severity': 'critical',
        'weight': 8,
        'category': 'Grammar & Language',
        'subcategory': 'Spelling',
        'auto_fixable': True,
        'display_name': 'Company/Brand Name Misspelled',
        'detection_method': 'nlp'
    },
    'GRAMMAR_GRAMMATICAL_ERROR': {
        'severity': 'critical',
        'weight': 8,
        'category': 'Grammar & Language',
        'subcategory': 'Grammar',
        'auto_fixable': True,
        'display_name': 'Grammatical Error',
        'detection_method': 'nlp'
    },
    'GRAMMAR_ARTICLE_MISUSE': {
        'severity': 'consider',
        'weight': 3,
        'category': 'Grammar & Language',
        'subcategory': 'Grammar',
        'auto_fixable': True,
        'display_name': 'Article Misuse (A/An/The)',
        'detection_method': 'nlp'
    },
    'GRAMMAR_INCONSISTENT_PERIODS': {
        'severity': 'consider',
        'weight': 2,
        'category': 'Grammar & Language',
        'subcategory': 'Punctuation',
        'auto_fixable': True,
        'display_name': 'Inconsistent Period Usage',
        'detection_method': 'regex'
    },
    'GRAMMAR_MISSING_PUNCTUATION': {
        'severity': 'consider',
        'weight': 3,
        'category': 'Grammar & Language',
        'subcategory': 'Punctuation',
        'auto_fixable': True,
        'display_name': 'Missing Punctuation',
        'detection_method': 'nlp'
    },
    'GRAMMAR_INCONSISTENT_TENSE': {
        'severity': 'important',
        'weight': 5,
        'category': 'Grammar & Language',
        'subcategory': 'Tense Consistency',
        'auto_fixable': True,
        'display_name': 'Inconsistent Verb Tense',
        'detection_method': 'nlp'
    },
    
    # ─────────────────────────────────────────────────────────────────
    # CATEGORY 5: LENGTH & CONCISENESS (4 types)
    # ─────────────────────────────────────────────────────────────────
    'LENGTH_CV_TOO_LONG': {
        'severity': 'important',
        'weight': 7,
        'category': 'Length & Conciseness',
        'subcategory': 'Overall Length',
        'auto_fixable': False,
        'display_name': 'CV is Too Long',
        'detection_method': 'rule'
    },
    'LENGTH_CV_TOO_SHORT': {
        'severity': 'consider',
        'weight': 5,
        'category': 'Length & Conciseness',
        'subcategory': 'Overall Length',
        'auto_fixable': False,
        'display_name': 'CV is Too Short',
        'detection_method': 'rule'
    },
    'LENGTH_EXPERIENCE_TOO_DETAILED': {
        'severity': 'consider',
        'weight': 4,
        'category': 'Length & Conciseness',
        'subcategory': 'Section Length',
        'auto_fixable': False,
        'display_name': 'Old Roles Have Too Much Detail',
        'detection_method': 'rule'
    },
    'LENGTH_EDUCATION_TOO_DETAILED': {
        'severity': 'consider',
        'weight': 3,
        'category': 'Length & Conciseness',
        'subcategory': 'Section Length',
        'auto_fixable': False,
        'display_name': 'Education Section Too Detailed',
        'detection_method': 'rule'
    },
    
    # ─────────────────────────────────────────────────────────────────
    # CATEGORY 6: PROFESSIONAL STANDARDS (8 types)
    # ─────────────────────────────────────────────────────────────────
    'STANDARDS_OBJECTIVE_STATEMENT': {
        'severity': 'important',
        'weight': 5,
        'category': 'Professional Standards',
        'subcategory': 'Outdated Elements',
        'auto_fixable': False,
        'display_name': 'Outdated Objective Statement',
        'detection_method': 'nlp'
    },
    'STANDARDS_REFERENCES_SECTION': {
        'severity': 'consider',
        'weight': 2,
        'category': 'Professional Standards',
        'subcategory': 'Outdated Elements',
        'auto_fixable': True,
        'display_name': 'Unnecessary References Section',
        'detection_method': 'regex'
    },
    'STANDARDS_OUTDATED_INFORMATION': {
        'severity': 'consider',
        'weight': 4,
        'category': 'Professional Standards',
        'subcategory': 'Outdated Elements',
        'auto_fixable': False,
        'display_name': 'Information Over 15 Years Old',
        'detection_method': 'rule'
    },
    'STANDARDS_OUTDATED_SKILLS': {
        'severity': 'important',
        'weight': 6,
        'category': 'Professional Standards',
        'subcategory': 'Outdated Elements',
        'auto_fixable': True,
        'display_name': 'Outdated Skills Listed',
        'detection_method': 'nlp'
    },
    'STANDARDS_HOBBIES_IRRELEVANT': {
        'severity': 'consider',
        'weight': 2,
        'category': 'Professional Standards',
        'subcategory': 'Unnecessary Sections',
        'auto_fixable': False,
        'display_name': 'Irrelevant Hobbies/Interests',
        'detection_method': 'nlp'
    },
    'STANDARDS_UNPROFESSIONAL_LANGUAGE': {
        'severity': 'important',
        'weight': 6,
        'category': 'Professional Standards',
        'subcategory': 'Professional Tone',
        'auto_fixable': True,
        'display_name': 'Unprofessional Language',
        'detection_method': 'nlp'
    },
    'STANDARDS_NEGATIVE_LANGUAGE': {
        'severity': 'important',
        'weight': 6,
        'category': 'Professional Standards',
        'subcategory': 'Professional Tone',
        'auto_fixable': False,
        'display_name': 'Negative Language',
        'detection_method': 'nlp'
    },
    
    # ─────────────────────────────────────────────────────────────────
    # CATEGORY 7: KEYWORDS & OPTIMIZATION (3 types)
    # ─────────────────────────────────────────────────────────────────
    'KEYWORDS_MISSING_INDUSTRY': {
        'severity': 'important',
        'weight': 7,
        'category': 'Keywords & Optimization',
        'subcategory': 'Industry Keywords',
        'auto_fixable': False,
        'display_name': 'Missing Industry Keywords',
        'detection_method': 'ai'
    },
    'KEYWORDS_SKILLS_FORMAT': {
        'severity': 'consider',
        'weight': 5,
        'category': 'Keywords & Optimization',
        'subcategory': 'Skill Keywords',
        'auto_fixable': True,
        'display_name': 'Skills Not ATS-Optimized',
        'detection_method': 'rule'
    },
    'KEYWORDS_ABBREVIATION_INCONSISTENT': {
        'severity': 'consider',
        'weight': 3,
        'category': 'Keywords & Optimization',
        'subcategory': 'Skill Keywords',
        'auto_fixable': True,
        'display_name': 'Inconsistent Abbreviation Usage',
        'detection_method': 'nlp'
    },
}

# ═══════════════════════════════════════════════════════════════════
# DEPRECATED: LEGACY_ISSUE_TYPE_MAPPING
# 
# This mapping has been moved to the database (cv_issue_legacy_mapping).
# The CatalogService now handles legacy code normalization.
# 
# Kept here for backward compatibility with severity.py.
# New code should use: catalog_service.normalize_issue_code()
# 
# Date deprecated: 2025-12-31
# ═══════════════════════════════════════════════════════════════════

LEGACY_ISSUE_TYPE_MAPPING = {
    'SPELLING_ERROR': 'GRAMMAR_SPELLING_ERROR',
    'GRAMMAR_ERROR': 'GRAMMAR_GRAMMATICAL_ERROR',
    'MISSING_EMAIL': 'CONTACT_MISSING_EMAIL',
    'MISSING_PHONE': 'CONTACT_MISSING_PHONE',
    'INVALID_EMAIL': 'CONTACT_UNPROFESSIONAL_EMAIL',
    'INVALID_PHONE': 'CONTACT_MISSING_PHONE',
    'MISSING_LINKEDIN': 'CONTACT_MISSING_LINKEDIN',
    'WEAK_SUMMARY': 'CONTENT_GENERIC_STATEMENTS',
    'SECTION_ORDER': 'FORMAT_POOR_VISUAL_HIERARCHY',
    'CV_TOO_LONG': 'LENGTH_CV_TOO_LONG',
    'CV_TOO_SHORT': 'LENGTH_CV_TOO_SHORT',
    'NO_METRICS': 'CONTENT_MISSING_METRICS',
    'BULLET_FORMAT': 'FORMAT_INCONSISTENT_BULLETS',
    'BULLET_TOO_LONG': 'CONTENT_BULLET_TOO_LONG',
    'BULLET_TOO_SHORT': 'CONTENT_BULLET_TOO_SHORT',
    'WEAK_ACTION_VERBS': 'CONTENT_WEAK_ACTION_VERBS',
    'VAGUE_DESCRIPTION': 'CONTENT_VAGUE_METRICS',
    'BUZZWORD_STUFFING': 'CONTENT_GENERIC_STATEMENTS',
    'DATE_FORMAT_INCONSISTENT': 'FORMAT_INCONSISTENT_DATES',
    'FORMAT_INCONSISTENT': 'FORMAT_INCONSISTENT_BULLETS',
    'WHITESPACE_ISSUE': 'FORMAT_TRAILING_WHITESPACE',
    'MINOR_FORMAT': 'FORMAT_MULTIPLE_SPACES',
    'OUTDATED_INFO': 'STANDARDS_OUTDATED_INFORMATION',
    'HEADER_STYLE': 'FORMAT_INCONSISTENT_CAPITALIZATION',
    'REPETITIVE_CONTENT': 'CONTENT_GENERIC_STATEMENTS',
}

# Default severity for unknown issue types (fallback)
DEFAULT_SEVERITY = 'consider'
DEFAULT_UI_CATEGORY = 'Content Quality'

# Valid severity levels (for validation) - NEW taxonomy
VALID_SEVERITIES = ['critical', 'important', 'consider', 'polish']

# Issue type enum list (for AI prompt reference)
ISSUE_TYPE_ENUM = list(ISSUE_TYPE_CONFIG.keys())
