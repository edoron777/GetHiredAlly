"""
Enhanced CV Parser - Main Module
Static parser using spaCy + regex + keyword matching
No AI/LLM dependencies - 100% deterministic
"""

import re
import os
import json
import spacy
import docx2txt
from pdfminer.high_level import extract_text as extract_pdf_text
from typing import Dict, List, Optional, Any
from .section_detector import detect_sections, SECTION_HEADERS
from .skills_extractor import extract_skills, load_skills_database

try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    import subprocess
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')


class EnhancedCVParser:
    """
    Enhanced CV Parser with section detection and skills extraction.
    100% static - no AI/LLM calls.
    """
    
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    PHONE_PATTERN = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
    LINKEDIN_PATTERN = r'linkedin\.com/in/[\w-]+'
    GITHUB_PATTERN = r'github\.com/[\w-]+'
    URL_PATTERN = r'https?://[^\s<>"\']+'
    
    EDUCATION_DEGREES = [
        'PhD', 'Ph.D.', 'Doctorate', 'Dr.',
        'MBA', 'M.B.A.', 'MA', 'M.A.', 'MS', 'M.S.', 'MSc', 'M.Sc.',
        'ME', 'M.E.', 'MTech', 'M.Tech', 'MCA', 'M.C.A.',
        'BA', 'B.A.', 'BS', 'B.S.', 'BSc', 'B.Sc.', 'BE', 'B.E.',
        'BTech', 'B.Tech', 'BBA', 'B.B.A.', 'BCA', 'B.C.A.',
        'Bachelor', 'Master', 'Associate', 'Diploma',
        'High School', 'GED', 'HSC', 'SSC', 'CBSE', 'ICSE'
    ]
    
    YEAR_PATTERN = r'(19|20)\d{2}'
    DATE_RANGE_PATTERN = r'(19|20)\d{2}\s*[-–—to]+\s*((19|20)\d{2}|present|current|now)'
    
    def __init__(self, skills_file_path: Optional[str] = None):
        """
        Initialize parser with optional custom skills file.
        
        Args:
            skills_file_path: Path to custom skills CSV file (optional)
        """
        self.skills_db = load_skills_database(skills_file_path)
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a CV file and extract structured data.
        
        Args:
            file_path: Path to CV file (PDF or DOCX)
            
        Returns:
            Dictionary with extracted CV data
        """
        raw_text = self._extract_text(file_path)
        
        if not raw_text or len(raw_text.strip()) < 50:
            return {
                'success': False,
                'error': 'Could not extract text from file or file is too short',
                'raw_text_length': len(raw_text) if raw_text else 0
            }
        
        doc = nlp(raw_text[:100000])
        
        contact_info = self._extract_contact_info(raw_text, doc)
        sections = detect_sections(raw_text)
        skills = extract_skills(raw_text, self.skills_db)
        education = self._extract_education(raw_text)
        experience_years = self._estimate_experience(raw_text)
        
        return {
            'success': True,
            'contact': contact_info,
            'sections': sections,
            'skills': skills,
            'education': education,
            'experience_years': experience_years,
            'raw_text_length': len(raw_text),
            'parser_version': '1.0-static'
        }
    
    def parse_text(self, text: str) -> Dict[str, Any]:
        """
        Parse CV from raw text (no file).
        
        Args:
            text: Raw CV text
            
        Returns:
            Dictionary with extracted CV data
        """
        if not text or len(text.strip()) < 50:
            return {
                'success': False,
                'error': 'Text is too short',
                'raw_text_length': len(text) if text else 0
            }
        
        doc = nlp(text[:100000])
        
        contact_info = self._extract_contact_info(text, doc)
        sections = detect_sections(text)
        skills = extract_skills(text, self.skills_db)
        education = self._extract_education(text)
        experience_years = self._estimate_experience(text)
        
        return {
            'success': True,
            'contact': contact_info,
            'sections': sections,
            'skills': skills,
            'education': education,
            'experience_years': experience_years,
            'raw_text_length': len(text),
            'parser_version': '1.0-static'
        }
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX file."""
        file_path_lower = file_path.lower()
        
        try:
            if file_path_lower.endswith('.pdf'):
                return extract_pdf_text(file_path)
            elif file_path_lower.endswith(('.docx', '.doc')):
                return docx2txt.process(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def _extract_contact_info(self, text: str, doc) -> Dict[str, Any]:
        """Extract contact information from CV."""
        emails = re.findall(self.EMAIL_PATTERN, text)
        
        phones = re.findall(self.PHONE_PATTERN, text)
        phones = [p.strip() for p in phones if len(re.sub(r'\D', '', p)) >= 7]
        
        linkedin_matches = re.findall(self.LINKEDIN_PATTERN, text, re.IGNORECASE)
        linkedin = linkedin_matches[0] if linkedin_matches else None
        
        github_matches = re.findall(self.GITHUB_PATTERN, text, re.IGNORECASE)
        github = github_matches[0] if github_matches else None
        
        name = self._extract_name(text, doc)
        
        return {
            'name': name,
            'email': emails[0] if emails else None,
            'phone': phones[0] if phones else None,
            'linkedin': linkedin,
            'github': github,
            'all_emails': emails[:3],
            'all_phones': phones[:3]
        }
    
    def _extract_name(self, text: str, doc) -> Optional[str]:
        """Extract person name from CV."""
        persons = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
        
        if persons:
            first_500 = text[:500]
            for person in persons:
                if person in first_500:
                    name = person.strip()
                    name = re.sub(r'\s*(CV|Resume|Curriculum Vitae).*$', '', name, flags=re.IGNORECASE)
                    if len(name) > 2 and len(name) < 50:
                        return name
        
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            if any(h in line.lower() for h in ['resume', 'cv', 'curriculum']):
                continue
            if '@' in line or re.search(r'\d{3}', line):
                continue
            words = line.split()
            if 2 <= len(words) <= 4 and all(w.replace('-', '').replace("'", '').isalpha() for w in words):
                return line
        
        return persons[0] if persons else None
    
    def _extract_education(self, text: str) -> Dict[str, Any]:
        """Extract education information."""
        found_degrees = []
        
        text_upper = text.upper()
        for degree in self.EDUCATION_DEGREES:
            pattern = r'\b' + re.escape(degree.upper()) + r'\b'
            if re.search(pattern, text_upper):
                found_degrees.append(degree)
        
        highest = None
        degree_rank = {
            'PhD': 5, 'Ph.D.': 5, 'Doctorate': 5, 'Dr.': 5,
            'MBA': 4, 'M.B.A.': 4, 'MA': 4, 'M.A.': 4, 'MS': 4, 'M.S.': 4,
            'MSc': 4, 'M.Sc.': 4, 'ME': 4, 'M.E.': 4, 'MTech': 4, 'M.Tech': 4,
            'Master': 4, 'MCA': 4, 'M.C.A.': 4,
            'BA': 3, 'B.A.': 3, 'BS': 3, 'B.S.': 3, 'BSc': 3, 'B.Sc.': 3,
            'BE': 3, 'B.E.': 3, 'BTech': 3, 'B.Tech': 3, 'Bachelor': 3,
            'BBA': 3, 'B.B.A.': 3, 'BCA': 3, 'B.C.A.': 3,
            'Associate': 2, 'Diploma': 2,
            'High School': 1, 'GED': 1, 'HSC': 1, 'SSC': 1
        }
        
        max_rank = 0
        for degree in found_degrees:
            rank = degree_rank.get(degree, 0)
            if rank > max_rank:
                max_rank = rank
                highest = degree
        
        return {
            'degrees_found': list(set(found_degrees)),
            'highest_degree': highest,
            'has_bachelors': max_rank >= 3,
            'has_masters': max_rank >= 4,
            'has_phd': max_rank >= 5
        }
    
    def _estimate_experience(self, text: str) -> Dict[str, Any]:
        """Estimate years of experience from date ranges."""
        years = [int(y) for y in re.findall(self.YEAR_PATTERN, text)]
        
        date_ranges = re.findall(self.DATE_RANGE_PATTERN, text, re.IGNORECASE)
        
        total_years = 0
        current_year = 2026
        
        for match in date_ranges:
            start_year = int(match[0])
            end_str = match[1].lower()
            
            if end_str in ['present', 'current', 'now']:
                end_year = current_year
            else:
                try:
                    year_match = re.search(r'(19|20)\d{2}', end_str)
                    end_year = int(year_match.group()) if year_match else current_year
                except:
                    end_year = current_year
            
            if 1970 <= start_year <= current_year and start_year <= end_year:
                total_years += (end_year - start_year)
        
        if total_years == 0 and years:
            valid_years = [y for y in years if 1970 <= y <= current_year]
            if len(valid_years) >= 2:
                total_years = max(valid_years) - min(valid_years)
        
        return {
            'estimated_years': min(total_years, 50),
            'years_mentioned': sorted(set(years)) if years else [],
            'date_ranges_found': len(date_ranges)
        }


def parse_cv(file_path: str, skills_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick function to parse a CV file.
    
    Args:
        file_path: Path to CV file
        skills_file: Optional path to custom skills CSV
        
    Returns:
        Parsed CV data as dictionary
    """
    parser = EnhancedCVParser(skills_file)
    return parser.parse(file_path)
