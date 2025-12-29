"""
CV Scoring Calibration Test
Uses Kaggle Resume Dataset to validate scoring algorithm
"""

import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.common.scoring import calculate_cv_score
from backend.common.scoring.extractors import extract_patterns, analyze_text

print("=" * 50)
print("STEP A: Loading Resume Dataset...")
print("=" * 50)

df = pd.read_csv('Temp/Resume.csv')

print(f"Total CVs: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nJob Categories: {df['Category'].unique() if 'Category' in df.columns else 'N/A'}")
print(f"\nSample CV (first 500 chars):")
print(df.iloc[0]['Resume_str'][:500] if 'Resume_str' in df.columns else df.iloc[0][0][:500])

print("\n" + "=" * 50)
print("STEP B: Scoring all CVs...")
print("=" * 50)

def extract_and_score(cv_text):
    """Extract features from CV text and calculate score."""
    try:
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
        return result.total_score
    except Exception as e:
        print(f"Error: {e}")
        return None

cv_column = 'Resume_str' if 'Resume_str' in df.columns else df.columns[0]

scores = []
for i, cv_text in enumerate(df[cv_column]):
    score = extract_and_score(cv_text)
    scores.append(score)
    if (i + 1) % 500 == 0:
        print(f"Scored {i + 1} / {len(df)} CVs...")

df['score'] = scores
print(f"\nScoring complete!")

print("\n" + "=" * 50)
print("STEP C: Score Distribution Analysis")
print("=" * 50)

valid_scores = [s for s in scores if s is not None]

print(f"CVs scored successfully: {len(valid_scores)} / {len(df)}")
print(f"\nScore Statistics:")
print(f"  Average: {sum(valid_scores) / len(valid_scores):.1f}")
print(f"  Minimum: {min(valid_scores)}")
print(f"  Maximum: {max(valid_scores)}")

ranges = [(0, 40), (40, 55), (55, 70), (70, 85), (85, 100)]
print(f"\nScore Distribution:")
for low, high in ranges:
    count = len([s for s in valid_scores if low <= s < high])
    pct = count / len(valid_scores) * 100
    bar = "█" * int(pct / 2)
    print(f"  {low:2d}-{high:2d}: {count:4d} ({pct:5.1f}%) {bar}")

if 'Category' in df.columns:
    print("\n" + "=" * 50)
    print("STEP D: Score by Job Category")
    print("=" * 50)
    
    category_scores = df.groupby('Category')['score'].agg(['mean', 'min', 'max', 'count'])
    category_scores = category_scores.sort_values('mean', ascending=False)
    
    print(f"\n{'Category':<25} {'Avg':>6} {'Min':>5} {'Max':>5} {'Count':>6}")
    print("-" * 50)
    for cat, row in category_scores.iterrows():
        print(f"{cat:<25} {row['mean']:>6.1f} {row['min']:>5.0f} {row['max']:>5.0f} {row['count']:>6.0f}")

print("\n" + "=" * 50)
print("STEP E: Saving Results")
print("=" * 50)

df.to_csv('Temp/resume_scores.csv', index=False)
print("Results saved to: Temp/resume_scores.csv")

print("\n" + "=" * 50)
print("CALIBRATION SUMMARY")
print("=" * 50)
print(f"""
Expected Distribution (healthy algorithm):
  - 10-20% should score 70+  (Good/Excellent)
  - 50-60% should score 50-70 (Fair)
  - 20-30% should score below 50 (Needs Work)

If most CVs score too HIGH → weights need reduction
If most CVs score too LOW → weights need increase
If all CVs score SIMILAR → algorithm lacks differentiation
""")
