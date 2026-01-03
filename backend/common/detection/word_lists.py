"""
Word Lists for Static CV Issue Detection

These lists are used by CODE to detect issues deterministically.
Same word → Same detection → Same result (ALWAYS)
"""

# ═══════════════════════════════════════════════════════════════════
# WEAK ACTION VERBS - Trigger WEAK_ACTION_VERBS issue
# ═══════════════════════════════════════════════════════════════════

WEAK_VERBS = [
    # Passive responsibility phrases
    "responsible for",
    "duties included",
    "duties include",
    "tasked with",
    "in charge of",
    "handled",
    "helped",
    "helped with",
    "assisted",
    "assisted with",
    "worked on",
    "worked with",
    "involved in",
    "involved with",
    "participated in",
    "was part of",
    "contributed to",
    
    # Weak verbs
    "did",
    "made",
    "got",
    "went",
    "used",
    "tried",
    "attempted",
    
    # Passive constructions
    "was responsible",
    "were responsible",
    "was tasked",
    "were tasked",
    "was assigned",
    "were assigned",
]

# ═══════════════════════════════════════════════════════════════════
# STRONG ACTION VERBS - For reference (good verbs)
# ═══════════════════════════════════════════════════════════════════

STRONG_VERBS = [
    # Leadership
    "led", "directed", "managed", "supervised", "coordinated",
    "orchestrated", "spearheaded", "headed", "oversaw", "guided",
    
    # Achievement
    "achieved", "accomplished", "delivered", "exceeded", "surpassed",
    "attained", "earned", "won", "secured", "captured",
    
    # Creation/Development
    "created", "developed", "designed", "built", "established",
    "launched", "initiated", "founded", "pioneered", "introduced",
    
    # Improvement
    "improved", "enhanced", "increased", "boosted", "optimized",
    "streamlined", "transformed", "revamped", "modernized", "upgraded",
    
    # Reduction (positive)
    "reduced", "decreased", "cut", "minimized", "eliminated",
    "consolidated", "simplified",
    
    # Analysis
    "analyzed", "evaluated", "assessed", "identified", "discovered",
    "investigated", "researched", "examined", "audited", "reviewed",
    
    # Communication
    "presented", "negotiated", "persuaded", "influenced", "advocated",
    "communicated", "collaborated", "partnered",
    
    # Implementation
    "implemented", "executed", "deployed", "integrated", "installed",
    "configured", "automated", "programmed", "engineered",
]

# ═══════════════════════════════════════════════════════════════════
# BUZZWORDS - Trigger BUZZWORD_STUFFING if too many
# ═══════════════════════════════════════════════════════════════════

BUZZWORDS = [
    "synergy", "synergize", "synergistic",
    "leverage", "leveraged", "leveraging",
    "paradigm", "paradigm shift",
    "disrupt", "disruptive", "disruption",
    "innovative", "innovation",
    "cutting-edge", "cutting edge",
    "best-in-class", "best in class",
    "world-class", "world class",
    "bleeding-edge", "bleeding edge",
    "game-changer", "game changer", "game-changing",
    "move the needle",
    "circle back",
    "deep dive",
    "thought leader", "thought leadership",
    "value-add", "value add", "added value",
    "scalable", "scalability",
    "holistic", "holistically",
    "proactive", "proactively",
    "dynamic", "dynamically",
    "robust", "robustness",
    "seamless", "seamlessly",
    "strategic", "strategically",
    "optimize", "optimization",
    "maximize", "maximization",
    "empower", "empowerment",
    "facilitate", "facilitation",
    "utilize", "utilization",
    "synergies",
    "bandwidth",
    "ecosystem",
    "actionable",
    "impactful",
]

BUZZWORD_THRESHOLD = 5  # More than this triggers BUZZWORD_STUFFING

# ═══════════════════════════════════════════════════════════════════
# VAGUE WORDS - Trigger VAGUE_DESCRIPTION issue
# ═══════════════════════════════════════════════════════════════════

VAGUE_WORDS = [
    "various",
    "several",
    "many",
    "multiple",
    "numerous",
    "some",
    "things",
    "stuff",
    "etc",
    "etc.",
    "and more",
    "and so on",
    "and others",
    "miscellaneous",
    "different",
    "certain",
    "a lot",
    "lots of",
    "a bunch",
    "kind of",
    "sort of",
    "somewhat",
    "basically",
    "generally",
    "usually",
    "often",
    "sometimes",
]

VAGUE_THRESHOLD = 3  # More than this triggers VAGUE_DESCRIPTION

# ═══════════════════════════════════════════════════════════════════
# FILLER PHRASES - Add no value
# ═══════════════════════════════════════════════════════════════════

FILLER_PHRASES = [
    "as needed",
    "as required",
    "when necessary",
    "on a daily basis",
    "on a regular basis",
    "day-to-day",
    "in order to",
    "for the purpose of",
    "with regard to",
    "in terms of",
    "at this point in time",
    "due to the fact that",
    "in the event that",
]

# ═══════════════════════════════════════════════════════════════════
# SECTION HEADERS - For section detection
# ═══════════════════════════════════════════════════════════════════

SUMMARY_HEADERS = [
    "summary", "professional summary", "executive summary",
    "profile", "professional profile", "career profile",
    "objective", "career objective", "job objective",
    "about", "about me", "introduction",
]

EXPERIENCE_HEADERS = [
    "experience", "work experience", "professional experience",
    "employment", "employment history", "work history",
    "career history", "positions held", "roles",
]

EDUCATION_HEADERS = [
    "education", "academic background", "educational background",
    "qualifications", "academic qualifications",
    "degrees", "certifications", "training",
]

SKILLS_HEADERS = [
    "skills", "technical skills", "core skills",
    "competencies", "core competencies", "key skills",
    "expertise", "areas of expertise", "proficiencies",
    "technologies", "tools", "languages",
]

# ═══════════════════════════════════════════════════════════════════
# DATE FORMATS - For date detection
# ═══════════════════════════════════════════════════════════════════

MONTH_NAMES = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept",
    "oct", "nov", "dec",
]

CURRENT_INDICATORS = [
    "present", "current", "now", "ongoing", "today",
]

# ═══════════════════════════════════════════════════════════════════════
# LENGTH THRESHOLDS (v1.5)
# Added: January 3, 2026
# Purpose: Constants for length-based detection of CV issues
# ═══════════════════════════════════════════════════════════════════════

# Professional Summary Thresholds
SUMMARY_MIN_WORDS = 30
SUMMARY_MAX_WORDS = 100
SUMMARY_MAX_SENTENCES = 5

# Bullet Point Thresholds
BULLET_MIN_WORDS = 10
BULLET_MAX_WORDS = 30

# Job Description Thresholds (per role)
JOB_DESCRIPTION_MIN_BULLETS = 3
JOB_DESCRIPTION_MAX_BULLETS = 8
JOB_DESCRIPTION_MIN_WORDS = 50
JOB_DESCRIPTION_MAX_WORDS = 200

# Education Entry Thresholds
EDUCATION_MIN_WORDS = 10
EDUCATION_EXPERIENCE_THRESHOLD = 3

# CV Overall Thresholds
CV_MIN_WORDS = 300
CV_MAX_WORDS_ONE_PAGE = 600
CV_MAX_WORDS_TWO_PAGES = 1200

# Skills Section Thresholds
SKILLS_POSITION_THRESHOLD = 0.4
