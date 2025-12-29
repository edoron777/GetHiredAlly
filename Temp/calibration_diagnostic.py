"""
CV Scoring Diagnostic - Find why scores cluster together
"""

import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.common.scoring import calculate_cv_score
from backend.common.scoring.extractors import extract_patterns, analyze_text

print("=" * 60)
print("DIAGNOSTIC: Why do all CVs score 55-70?")
print("=" * 60)

df = pd.read_csv('Temp/Resume.csv')
cv_column = 'Resume_str' if 'Resume_str' in df.columns else df.columns[0]

print("\nAnalyzing 20 CVs in detail...\n")

category_totals = {
    "grammar": [],
    "formatting": [],
    "quantification": [],
    "language": [],
    "contact": [],
    "skills": [],
    "experience": [],
    "length": []
}

for i in range(20):
    cv_text = str(df.iloc[i][cv_column])
    
    patterns = extract_patterns(cv_text)
    text_metrics = analyze_text(cv_text)
    
    if i < 3:
        print(f"\n--- CV #{i+1} (first 200 chars) ---")
        print(cv_text[:200])
        print(f"\nExtracted patterns:")
        print(f"  has_email: {patterns.get('has_email')}")
        print(f"  has_phone: {patterns.get('has_phone')}")
        print(f"  has_linkedin: {patterns.get('has_linkedin')}")
        print(f"  has_section_headers: {patterns.get('has_section_headers')}")
        print(f"  strong_action_verbs_count: {patterns.get('strong_action_verbs_count')}")
        print(f"  weak_phrases_count: {patterns.get('weak_phrases_count')}")
        print(f"  bullets_with_numbers: {patterns.get('bullets_with_numbers')}")
        print(f"\nText metrics:")
        print(f"  word_count: {text_metrics.get('word_count')}")
        print(f"  total_bullet_points: {text_metrics.get('total_bullet_points')}")
    
    extracted_data = {
        "has_name": True,
        "has_email": patterns.get("has_email", False),
        "has_phone": patterns.get("has_phone", False),
        "has_linkedin": patterns.get("has_linkedin", False),
        "email_is_professional": True,
        "has_section_headers": patterns.get("has_section_headers", False),
        "uses_bullet_points": text_metrics.get("total_bullet_points", 0) > 0,
        "has_skills_section": True,
        "skills_are_categorized": False,
        "page_count": text_metrics.get("estimated_page_count", 1),
        "word_count": text_metrics.get("word_count", 0),
        "total_bullet_points": text_metrics.get("total_bullet_points", 0),
        "bullets_with_numbers": patterns.get("bullets_with_numbers", 0),
        "strong_action_verbs_count": patterns.get("strong_action_verbs_count", 0),
        "weak_phrases_count": patterns.get("weak_phrases_count", 0),
        "passive_voice_count": patterns.get("passive_voice_count", 0),
        "grammar_errors_count": 0,
        "spelling_errors_count": 0,
        "has_dates_for_each_role": True,
        "dates_are_consistent_format": True,
        "is_reverse_chronological": True,
        "has_company_names": True,
        "has_job_titles": True,
        "tech_keywords_found": []
    }
    
    result = calculate_cv_score(extracted_data)
    
    breakdown = result.breakdown.to_dict()
    for cat, score in breakdown.items():
        category_totals[cat].append(score)

print("\n" + "=" * 60)
print("CATEGORY SCORE ANALYSIS (first 20 CVs)")
print("=" * 60)

print(f"\n{'Category':<20} {'Avg':>8} {'Min':>8} {'Max':>8} {'Range':>8} {'Max Possible':>12}")
print("-" * 70)

max_points = {
    "grammar": 10,
    "formatting": 12,
    "quantification": 25,
    "language": 15,
    "contact": 5,
    "skills": 13,
    "experience": 15,
    "length": 5
}

for cat, scores in category_totals.items():
    avg = sum(scores) / len(scores)
    mn = min(scores)
    mx = max(scores)
    rng = mx - mn
    max_p = max_points.get(cat, 10)
    
    flag = " ⚠️ NO VARIATION" if rng < 2 else ""
    
    print(f"{cat:<20} {avg:>8.1f} {mn:>8.1f} {mx:>8.1f} {rng:>8.1f} {max_p:>12}{flag}")

print("\n" + "=" * 60)
print("PROBLEMS IDENTIFIED")
print("=" * 60)

problems = []

for cat, scores in category_totals.items():
    rng = max(scores) - min(scores)
    if rng < 3:
        problems.append(f"- {cat}: Range only {rng:.1f} points (no differentiation)")

if problems:
    print("\nCategories with NO differentiation:")
    for p in problems:
        print(p)
else:
    print("\nAll categories show good variation")

print("\n" + "=" * 60)
print("RECOMMENDED FIXES")
print("=" * 60)
print("""
1. STOP assuming these are True:
   - has_skills_section → Detect from text
   - has_dates_for_each_role → Detect from text
   - is_reverse_chronological → Detect from text
   - has_company_names → Detect from text
   - has_job_titles → Detect from text

2. Add more extractors:
   - Detect skills section presence
   - Detect date patterns
   - Detect company/title patterns
   
3. Widen the scoring ranges:
   - Currently most categories give middle scores
   - Need more extreme penalties/bonuses
""")
