"""
Pattern Matcher - Deterministic regex-based detection
Version: 4.0

All pattern matching is DETERMINISTIC - same text = same results.
"""

import re
from typing import List, Dict, Any


class PatternMatcher:
    """Deterministic pattern detection for CV analysis."""
    
    # Regex patterns for detection
    PATTERNS = {
        # Contact information
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'\+?\d{1,3}[-.\s]?\(?\d{2,3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        'linkedin': r'linkedin\.com/in/[\w-]+',
        'github': r'github\.com/[\w-]+',
        
        # Quantification
        'percentage': r'\d+%',
        'currency': r'\$[\d,]+[KMB]?',
        'team_size': r'team of \d+|\d+\s*(team members|engineers|developers|people|reports)',
        'time_metric': r'\d+\s*(months?|years?|weeks?|days?)',
        'project_count': r'\d+\s*projects?',
        'user_count': r'\d+[,\d]*\s*(users?|customers?|clients?|patients?|students?)',
        'any_number': r'\b\d+\b',
        
        # Structure
        'section_header': r'^(About|Summary|Profile|Experience|Work Experience|Education|Skills|Technical Skills|Certifications|Projects|Awards|Languages|Interests)',
        'bullet_point': r'^[\•\-\*\○\►]\s',
        'date_format': r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b|\b\d{1,2}/\d{4}\b|\b\d{4}\s*[-–]\s*(Present|\d{4})\b',
        
        # Red flags
        'unprofessional_email': r'(sexy|hot|babe|party|420|princess|gangster|killer|xoxo|cutie|lover|ninja|pimp)\d*@',
        'personal_info': r'\b(age|date of birth|dob|marital status|religion|nationality)\b',
        'salary_mention': r'\$([\d,]+)\s*(per|/)\s*(year|month|hour|annum)|salary|compensation',
    }
    
    @classmethod
    def find_all(cls, pattern_name: str, text: str) -> List[str]:
        """
        Find all matches for a named pattern.
        
        DETERMINISTIC: Same text = Same results.
        
        Args:
            pattern_name: Key from PATTERNS dict
            text: Text to search
        
        Returns:
            List of all matches
        """
        pattern = cls.PATTERNS.get(pattern_name)
        if not pattern:
            return []
        return re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
    
    @classmethod
    def count(cls, pattern_name: str, text: str) -> int:
        """
        Count matches for a pattern.
        
        DETERMINISTIC: Same text = Same count.
        """
        return len(cls.find_all(pattern_name, text))
    
    @classmethod
    def has_match(cls, pattern_name: str, text: str) -> bool:
        """
        Check if pattern exists in text.
        
        DETERMINISTIC: Same text = Same boolean.
        """
        return cls.count(pattern_name, text) > 0
    
    @classmethod
    def count_words(cls, text: str) -> int:
        """Count words in text. DETERMINISTIC."""
        return len(text.split())
    
    @classmethod
    def count_bullets(cls, text: str) -> int:
        """Count bullet points. DETERMINISTIC."""
        # Count lines starting with bullet characters
        lines = text.split('\n')
        count = 0
        for line in lines:
            stripped = line.strip()
            if stripped and stripped[0] in '•-*○►':
                count += 1
        return count
    
    @classmethod
    def find_word_frequency(cls, text: str, min_count: int = 5) -> Dict[str, int]:
        """
        Find words that appear frequently.
        
        Args:
            text: Text to analyze
            min_count: Minimum occurrences to include
        
        Returns:
            Dictionary of word -> count for frequent words
        """
        # Simple word extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Count occurrences
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        
        # Filter by min_count
        return {w: c for w, c in freq.items() if c >= min_count}
    
    @classmethod
    def check_verb_at_start(cls, bullet_text: str, verb_list: List[str]) -> bool:
        """
        Check if bullet starts with a verb from the list.
        
        DETERMINISTIC.
        """
        # Get first word
        words = bullet_text.strip().split()
        if not words:
            return False
        
        first_word = words[0].strip('•-*○► ').capitalize()
        return first_word in verb_list
    
    @classmethod
    def extract_all_metrics(cls, text: str) -> Dict[str, List[str]]:
        """
        Extract all quantification metrics from text.
        
        Returns:
            Dictionary with metric types and their values
        """
        return {
            'percentages': cls.find_all('percentage', text),
            'currency': cls.find_all('currency', text),
            'team_sizes': cls.find_all('team_size', text),
            'time_metrics': cls.find_all('time_metric', text),
            'project_counts': cls.find_all('project_count', text),
            'user_counts': cls.find_all('user_count', text)
        }
