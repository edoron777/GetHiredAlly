# CV Optimizer Naming Conventions

This document defines the official naming conventions for all UI elements, sections, and components in the CV Optimizer feature.

---

## Page Names

| Route | Official Page Name | Purpose |
|-------|-------------------|---------|
| /service/cv-optimizer | Upload Page | CV file upload |
| /service/cv-optimizer/scanning | Scanning Page | Analysis in progress |
| /service/cv-optimizer/results/{id} | Results Summary | Quick score overview |
| /service/cv-optimizer/report/{id} | Report Page | Detailed analysis |
| /service/cv-optimizer/fix/{id} | Fix Results Page | Improved CV comparison |

---

## Report Page Structure

### Section Names

| Section ID | Official Name | UI Header | Description |
|------------|---------------|-----------|-------------|
| score_overview | Score Overview | "Step 1: Your CV Score" | Circular gauge + message |
| score_breakdown | Score Breakdown | "Score Breakdown" | Category progress bars |
| category_filter | Category Filter | "Filter Results by Category" | Checkbox grid |
| detail_level | Detail Level | "Choose your detail level" | Depth dropdown |
| severity_filter | Severity Filter | (integrated with list) | Priority tabs/sections |
| recommendations_list | Recommendations List | "Step 2: Analysis & Recommendations" | Grouped issues |
| action_bar | Action Bar | (no header) | Export/share buttons |

### Section Headers

| Page | Section | Header Text |
|------|---------|-------------|
| Report | Score Display | "Step 1: Your CV Score" |
| Report | Category Bars | "Score Breakdown" |
| Report | Recommendations | "Step 2: Analysis & Recommendations" |
| Report | Category Filter | "Filter Results by Category" |
| Report | Detail Level | "Choose your detail level" |
| Report | Priority Group (Critical) | "FIX NOW" |
| Report | Priority Group (High) | "SHOULD ADDRESS" |
| Report | Priority Group (Medium) | "WORTH CONSIDERING" |
| Report | Priority Group (Low) | "OPTIONAL POLISH" |
| Fix Results | Score Comparison | "Score Improvement" |
| Fix Results | CV Comparison | "Before & After" |
| Fix Results | Download Section | "Download Your Improved CV" |

---

## Priority Levels (Severity Groups)

| Level | Code | UI Display | Color Code | Description |
|-------|------|------------|------------|-------------|
| 1 | critical | "FIX NOW" | #EF4444 (red) | Must fix before applying |
| 2 | high | "SHOULD ADDRESS" | #F97316 (orange) | Important improvements |
| 3 | medium | "WORTH CONSIDERING" | #EAB308 (yellow) | Recommended improvements |
| 4 | low | "OPTIONAL POLISH" | #22C55E (green) | Nice-to-have refinements |

---

## Effort Indicators

| Level | Code | UI Display | Icon | Description |
|-------|------|------------|------|-------------|
| 1 | quick | "Quick fix" | ⚡ | Less than 2 minutes to fix |
| 2 | medium | "Medium effort" | 🔧 | 2-10 minutes to fix |
| 3 | extensive | "Requires rewrite" | 📝 | Significant changes needed |

---

## Scoring Categories (v4.0)

| Category ID | Display Name | Max Points | Description |
|-------------|--------------|------------|-------------|
| content_quality | Content Quality | 40 | Achievements, metrics, impact |
| language_clarity | Language & Clarity | 18 | Action verbs, conciseness |
| formatting | Formatting & Structure | 18 | Layout, consistency, readability |
| completeness | Completeness | 12 | Required sections, information |
| professional | Professional Presentation | 8 | Email, consistency, tone |
| red_flags | Red Flag Avoidance | 4 | No typos, gaps explained |

**Total: 100 points**

---

## Recommendation Card Structure

```
┌─────────────────────────────────────────────────────────────┐
│ ▶ [Issue Title]                          [Effort Indicator] │
│   "Missing LinkedIn URL"                      ⚡ Quick fix   │
├─────────────────────────────────────────────────────────────┤
│ (Expanded Content - shown when clicked)                     │
│                                                             │
│ [Issue Description]                                         │
│ "Adding a LinkedIn URL helps recruiters verify your..."     │
│                                                             │
│ [Example Section] (if detail level >= 2)                    │
│ ✅ Correct: "linkedin.com/in/yourname"                      │
│ ❌ Avoid: (if detail level >= 3)                            │
│                                                             │
│ [Category Badge]                                            │
│ 📋 Contact Information                                       │
└─────────────────────────────────────────────────────────────┘
```

| Element | Name | Always Visible |
|---------|------|----------------|
| Expand Icon | Toggle Arrow | Yes |
| Main Text | Issue Title | Yes |
| Right Badge | Effort Indicator | Yes |
| Body Text | Issue Description | On expand |
| Good Example | Correct Example | On expand (level 2+) |
| Bad Example | Avoid Example | On expand (level 3+) |
| Bottom Tag | Category Badge | On expand |

---

## UI Element Names

### Buttons

| Element | Official Name | UI Text |
|---------|---------------|---------|
| Primary CTA | Generate Fix | "Generate AI-Powered Fix" |
| Export PDF | Download PDF | "Download PDF" |
| Export Word | Download Word | "Download Word" |
| Share Email | Email Report | "Email" |
| Share WhatsApp | Share WhatsApp | "WhatsApp" |

### Interactive Elements

| Element | Official Name | Description |
|---------|---------------|-------------|
| Score Gauge | Score Circle | Animated circular progress |
| Category Bar | Progress Bar | Horizontal category score |
| Filter Checkbox | Category Toggle | Enable/disable category |
| Expand/Collapse | Accordion Toggle | Show/hide issue details |

---

## Grade Labels

| Score Range | Grade Code | Display Label |
|-------------|------------|---------------|
| 90-100 | excellent | "Excellent" |
| 75-89 | good | "Good" |
| 60-74 | fair | "Fair" |
| 45-59 | needs_work | "Needs Work" |
| 0-44 | poor | "Poor" |

---

## File Naming

| File Type | Naming Pattern | Example |
|-----------|----------------|---------|
| PDF Export | CV_Report_{date}.pdf | CV_Report_2025-01-15.pdf |
| Word Export | CV_Report_{date}.docx | CV_Report_2025-01-15.docx |
| Fixed CV PDF | CV_Optimized_{date}.pdf | CV_Optimized_2025-01-15.pdf |
| Fixed CV Word | CV_Optimized_{date}.docx | CV_Optimized_2025-01-15.docx |

---

## API Response Keys

| Key | Description | Type |
|-----|-------------|------|
| score | Total CV score (0-100) | integer |
| breakdown | Category scores object | object |
| grade | Grade code (excellent, good, etc.) | string |
| grade_label | Display-friendly grade | string |
| message | Score explanation | string |
| issues | List of recommendations | array |
| issues_count | Total number of issues | integer |

---

*Last Updated: December 30, 2025*
*Scoring Version: 4.0*
