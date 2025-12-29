"""
CV Scoring Diagnostic
Analyze WHY all scores are similar
"""

import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.common.scoring import calculate_cv_score
from backend.common.scoring.extractors import extract_patterns, analyze_text
from backend.common.scoring.config import CATEGORY_WEIGHTS

print("=" * 60)
print("DIAGNOSTIC: Why are all CV scores similar?")
print("=" * 60)

df = pd.read_csv('Temp/Resume.csv')
sample_cvs = df['Resume_str'].head(20).tolist()

all_extractions = []

for i, cv_text in enumerate(sample_cvs):
    patterns = extract_patterns(str(cv_text))
    text_metrics = analyze_text(str(cv_text))
    
    extraction = {
        "cv_num": i + 1,
        "word_count": text_metrics.get("word_count", 0),
        "bullet_points": text_metrics.get("total_bullet_points", 0),
        "has_email": patterns.get("has_email", False),
        "has_phone": patterns.get("has_phone", False),
        "has_linkedin": patterns.get("has_linkedin", False),
        "has_section_headers": patterns.get("has_section_headers", False),
        "bullets_with_numbers": patterns.get("bullets_with_numbers", 0),
        "strong_action_verbs": patterns.get("strong_action_verbs_count", 0),
        "weak_phrases": patterns.get("weak_phrases_count", 0),
        "passive_voice": patterns.get("passive_voice_count", 0),
    }
    all_extractions.append(extraction)

print("\n" + "=" * 60)
print("STEP 1: What features are we extracting?")
print("=" * 60)

df_ext = pd.DataFrame(all_extractions)
print("\nFeature Values (first 20 CVs):")
print(df_ext.to_string())

print("\n" + "=" * 60)
print("STEP 2: Feature Statistics")
print("=" * 60)

for col in df_ext.columns:
    if col == "cv_num":
        continue
    values = df_ext[col]
    if values.dtype == bool:
        true_count = values.sum()
        print(f"{col:25s}: {true_count}/20 are True ({true_count/20*100:.0f}%)")
    else:
        print(f"{col:25s}: min={values.min():5}, max={values.max():5}, avg={values.mean():.1f}")

print("\n" + "=" * 60)
print("STEP 3: Category Score Breakdown (first 5 CVs)")
print("=" * 60)

for i, cv_text in enumerate(sample_cvs[:5]):
    patterns = extract_patterns(str(cv_text))
    text_metrics = analyze_text(str(cv_text))
    
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
    
    print(f"\n--- CV #{i+1} (Score: {result.total_score}) ---")
    print(f"Word count: {extracted_data['word_count']}, Bullets: {extracted_data['total_bullet_points']}")
    for cat, weight in CATEGORY_WEIGHTS.items():
        cat_score = result.breakdown.to_dict().get(cat, 0)
        pct = (cat_score / weight * 100) if weight > 0 else 0
        bar = "█" * int(pct / 10)
        print(f"  {cat:15s}: {cat_score:5.1f}/{weight:2d} ({pct:5.1f}%) {bar}")

print("\n" + "=" * 60)
print("STEP 4: Hardcoded Assumptions Analysis")
print("=" * 60)

hardcoded = {
    "has_name": "Always True",
    "email_is_professional": "Always True",
    "has_skills_section": "Always True",
    "has_dates_for_each_role": "Always True",
    "dates_are_consistent_format": "Always True",
    "is_reverse_chronological": "Always True",
    "has_company_names": "Always True",
    "has_job_titles": "Always True",
    "grammar_errors_count": "Always 0",
    "spelling_errors_count": "Always 0",
    "skills_are_categorized": "Always False",
}

print("\nThese values are HARDCODED (not extracted from CV):")
for field, value in hardcoded.items():
    print(f"  {field:30s} = {value}")

print("\n" + "=" * 60)
print("DIAGNOSIS SUMMARY")
print("=" * 60)
print("""
LIKELY CAUSES of low differentiation:

1. TOO MANY HARDCODED VALUES
   - 11 fields are hardcoded (not extracted)
   - These guarantee similar base scores

2. LIMITED EXTRACTION
   - Only extracting basic patterns (email, phone, etc)
   - Not detecting actual CV quality differences

3. CATEGORY SCORING FLOORS
   - Most categories give partial credit even with issues
   - Creates a ~60 baseline that's hard to deviate from

RECOMMENDATIONS:
   - Remove hardcoded assumptions
   - Add more extractors for quality signals
   - Increase penalty for missing features
   - Add variance to quantification scoring
""")
