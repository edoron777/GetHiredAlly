"""
Data models for CV Scoring.
"""

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class IssueCategory(str, Enum):
    GRAMMAR = "grammar"
    FORMATTING = "formatting"
    QUANTIFICATION = "quantification"
    LANGUAGE = "language"
    CONTACT = "contact"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    LENGTH = "length"
    TAILORING = "tailoring"


class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ScoreBreakdown:
    """Score breakdown by category."""
    grammar: float = 0.0
    formatting: float = 0.0
    quantification: float = 0.0
    language: float = 0.0
    contact: float = 0.0
    skills: float = 0.0
    experience: float = 0.0
    length: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "grammar": round(self.grammar, 1),
            "formatting": round(self.formatting, 1),
            "quantification": round(self.quantification, 1),
            "language": round(self.language, 1),
            "contact": round(self.contact, 1),
            "skills": round(self.skills, 1),
            "experience": round(self.experience, 1),
            "length": round(self.length, 1)
        }
    
    def total(self) -> float:
        return sum([
            self.grammar, self.formatting, self.quantification,
            self.language, self.contact, self.skills,
            self.experience, self.length
        ])


@dataclass
class ScoreResult:
    """Complete scoring result."""
    total_score: int
    breakdown: ScoreBreakdown
    grade: str
    message: str
    version: str = "1.0.0"
    max_possible: int = 95
    
    def to_dict(self) -> Dict:
        return {
            "total_score": self.total_score,
            "breakdown": self.breakdown.to_dict(),
            "grade": self.grade,
            "message": self.message,
            "version": self.version,
            "max_possible": self.max_possible
        }


@dataclass
class ExtractedData:
    """Data extracted from CV for scoring."""
    # Contact info
    has_name: bool = False
    has_email: bool = False
    has_phone: bool = False
    has_linkedin: bool = False
    email_is_professional: bool = False
    
    # Structure
    has_section_headers: bool = False
    uses_bullet_points: bool = False
    has_skills_section: bool = False
    skills_are_categorized: bool = False
    
    # Metrics
    page_count: int = 1
    word_count: int = 0
    total_bullet_points: int = 0
    bullets_with_numbers: int = 0
    
    # Language quality
    strong_action_verbs_count: int = 0
    weak_phrases_count: int = 0
    passive_voice_count: int = 0
    grammar_errors_count: int = 0
    spelling_errors_count: int = 0
    
    # Experience
    has_dates_for_each_role: bool = False
    dates_are_consistent_format: bool = False
    is_reverse_chronological: bool = False
    has_company_names: bool = False
    has_job_titles: bool = False
    
    # Tech specific
    tech_keywords_found: List[str] = field(default_factory=list)
