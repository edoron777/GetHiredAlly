"""
CV Scoring Configuration
All weights, thresholds, and constants.
Version: 1.1.0
"""

# Version - increment when changing weights
SCORING_VERSION = "1.1.0"

# Score boundaries
SCORE_MIN = 15   # Never show 0 (too demoralizing)
SCORE_MAX = 95   # Never show 100 (no CV is perfect)
AFTER_FIX_MAX = 88  # Cap for after-fix score (realistic improvement)

# Category weights (must sum to 100)
CATEGORY_WEIGHTS = {
    "grammar": 10,
    "formatting": 12,
    "quantification": 25,
    "language": 15,
    "contact": 5,
    "skills": 13,
    "experience": 15,
    "length": 5
}

# Validate weights sum to 100
assert sum(CATEGORY_WEIGHTS.values()) == 100, "Weights must sum to 100"

# Grade thresholds
GRADE_THRESHOLDS = {
    "excellent": 82,
    "good": 68,
    "fair": 52,
    "needs_work": 35
}

# Grade messages
GRADE_MESSAGES = {
    "excellent": "Outstanding! Your CV is highly polished and ready to impress recruiters.",
    "good": "Great CV! A few small improvements will make it even stronger.",
    "fair": "Good foundation. Addressing the suggestions below will help you stand out.",
    "needs_work": "Your CV has room for improvement. Focus on the high-priority items.",
    "needs_attention": "Let's strengthen your CV. Start with the critical issues for maximum impact."
}

# Fixability rates for after-fix calculation
FIXABILITY_RATES = {
    "grammar": 0.70,
    "formatting": 0.60,
    "language": 0.65,
    "quantification": 0.35,
    "skills": 0.40,
    "contact": 0.80,
    "experience": 0.15,
    "length": 0.50
}
