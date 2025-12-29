# X-Ray Analyzer Service Documentation

**Generated:** December 29, 2025  
**Purpose:** Complete technical documentation for the "Decode the Job Post" (X-Ray Analyzer) service

---

## 1. ALL FILES USED

### Frontend Files

| File Path | Main Functions |
|-----------|----------------|
| `client/src/components/UnderstandJobPage.tsx` | **Main UI Component** - Job description input, interviewer type selection, depth level selection, AI provider selection, analysis display, markdown rendering |
| `client/src/components/AIProviderSelector.tsx` | AI provider toggle (Claude/Gemini) |
| `client/src/components/common/StandardToolbar.tsx` | Export toolbar (PDF, Word, Markdown, Email, WhatsApp sharing) |

### Backend Files

| File Path | Main Functions |
|-----------|----------------|
| `backend/app/analyze.py` | **Main Backend Logic** - API endpoint `/api/analyze-job`, prompt assembly from DB or fallbacks, response parsing (markdown + JSON), database save |
| `backend/services/ai_service.py` | Unified AI completion service - routes to Claude or Gemini via LiteLLM, logs usage |
| `backend/app/main.py` | Includes analyze_router |

### Shared/Config Files

| File Path | Purpose |
|-----------|---------|
| `backend/config/rate_limiter.py` | Rate limiting (20/hour for analyze endpoint) |

---

## 2. DATABASE TABLES

### Table: `job_descriptions`

| Column Name | Data Type | Nullable | Default |
|-------------|-----------|----------|---------|
| id | integer | NO | nextval('job_descriptions_id_seq') |
| user_id | uuid | YES | - |
| job_description | text | NO | - |
| analysis | text | YES | - |
| interviewer_type | character varying | YES | - |
| depth_level | character varying | YES | - |
| provider | character varying | YES | - |
| created_at | timestamp with time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp with time zone | YES | CURRENT_TIMESTAMP |

### Table: `analysis_results`

| Column Name | Data Type | Nullable | Default |
|-------------|-----------|----------|---------|
| id | uuid | NO | gen_random_uuid() |
| session_id | uuid | YES | - |
| report_markdown | text | YES | - |
| structured_data | jsonb | YES | - |
| validation_status | text | YES | - |
| validation_details | jsonb | YES | - |
| created_at | timestamp without time zone | YES | now() |

### Table: `analysis_sessions`

| Column Name | Data Type | Nullable | Default |
|-------------|-----------|----------|---------|
| id | uuid | NO | gen_random_uuid() |
| user_id | uuid | YES | - |
| service_name | text | NO | - |
| job_description_text | text | NO | - |
| job_title | text | YES | - |
| company_name | text | YES | - |
| mode | text | NO | - |
| created_at | timestamp without time zone | YES | now() |

### Table: `prompt_templates`

| Column Name | Data Type | Nullable | Default |
|-------------|-----------|----------|---------|
| id | uuid | NO | gen_random_uuid() |
| service_name | text | NO | - |
| mode | text | NO | - |
| template_type | text | NO | - |
| category_id | integer | YES | - |
| content | text | NO | - |
| version | integer | YES | 1 |
| is_active | boolean | YES | true |
| created_at | timestamp without time zone | YES | now() |
| updated_at | timestamp without time zone | YES | now() |

---

## 3. PROMPT TEMPLATES

### Database Status

**NOTE:** The development database currently has **0 rows** in `prompt_templates` for `service_name = 'xray_analyzer'`.

The production database has **8 prompts** for xray_analyzer (based on logs showing prompts are found).

### Expected Template Types for X-Ray Analyzer

| template_type | Purpose |
|---------------|---------|
| system_v2 | Base system prompt defining the AI's role |
| interviewer_hr | HR/Recruiter focus prompt |
| interviewer_technical | Technical interviewer focus prompt |
| interviewer_manager | Hiring manager focus prompt |
| interviewer_general | General preparation prompt |
| depth_ready | "Interview Ready" concise output format |
| depth_full | "Fully Prepared" comprehensive output format |

---

## 4. FALLBACK PROMPTS (Used when DB prompts not available)

### FALLBACK_SYSTEM_PROMPT

```
You are an expert career coach and interview preparation specialist with 20+ years of experience helping candidates land their dream jobs. Your role is to provide detailed, actionable analysis that gives candidates a real competitive advantage.

Your analysis style is:
- Direct and practical, not generic
- Specific to the role and company
- Focused on what will actually help in the interview
- Honest about red flags or concerns

Always structure your response clearly with headers and bullet points for easy reading.
```

### FALLBACK_INTERVIEWER_PROMPTS

#### HR / Recruiter (`interviewer_hr`)

```
INTERVIEWER FOCUS: HR / Recruiter Screen

Since this is an HR/Recruiter interview, emphasize:
- Cultural fit and soft skills they're looking for
- Salary expectations and benefits signals in the posting
- Work-life balance and company culture indicators
- Screening questions they're likely to ask
- How to present your career story compellingly
- Red flags in your background to address proactively
```

#### Technical (`interviewer_technical`)

```
INTERVIEWER FOCUS: Technical Interview

Since this is a Technical interview, emphasize:
- Specific technical skills and tools mentioned
- Experience levels required for each technology
- Types of technical problems they likely solve
- System design or architecture expectations
- Coding challenge topics to prepare
- Technical questions to ask about their stack
```

#### Hiring Manager (`interviewer_manager`)

```
INTERVIEWER FOCUS: Hiring Manager Interview

Since this is a Hiring Manager interview, emphasize:
- Team dynamics and collaboration style
- Deliverables and success metrics for the role
- Management style and autonomy level
- Growth opportunities and career path
- Challenges the team is facing
- How to demonstrate you'll make their life easier
```

#### General (`interviewer_general`)

```
INTERVIEWER FOCUS: General Preparation

Since you're not sure who will interview you, prepare for all angles:
- Technical skills and how you'll demonstrate them
- Behavioral questions and STAR format stories
- Cultural fit and soft skills
- Questions about your background and motivations
- Salary and benefits conversation preparation
```

### FALLBACK_DEPTH_PROMPTS

#### Interview Ready (`depth_ready`)

```
OUTPUT FORMAT: Interview Ready (Concise)

Provide a FOCUSED analysis covering the essentials:
- 5-7 key requirements to highlight
- 3-4 likely interview questions with answer frameworks
- Top 3 things that will make you stand out
- 2-3 smart questions to ask them

Keep your response between 600-900 words. Be direct and actionable.
```

#### Fully Prepared (`depth_full`)

```
OUTPUT FORMAT: Fully Prepared (Comprehensive)

Provide a THOROUGH analysis covering everything:

1. **Role Overview** - What this role really involves
2. **Must-Have Skills** - Non-negotiable requirements
3. **Nice-to-Have Skills** - Differentiators to highlight
4. **Hidden Expectations** - Reading between the lines
5. **Company Culture Signals** - What the language tells us
6. **Red Flags & Concerns** - Things to clarify
7. **Interview Questions** - 8-10 likely questions with answer guidance
8. **Your Talking Points** - Key themes to weave into answers
9. **Questions to Ask Them** - Smart questions that impress
10. **Preparation Checklist** - Specific things to do before the interview

Provide 1500-2000 words of detailed, actionable guidance.
```

### JSON_STRUCTURE_SUFFIX (Appended to depth prompts)

```
---

IMPORTANT: After your markdown report, you MUST include a structured JSON block.

Use this EXACT format:

---JSON_DATA_START---
{
  "company_name": "extracted company name or null",
  "job_title": "extracted job title",
  "seniority_level": "junior/mid/senior/lead/executive",
  "key_requirements": ["requirement 1", "requirement 2", "requirement 3"],
  "technical_skills": [
    {"skill": "skill name", "importance": "required/preferred/nice-to-have"}
  ],
  "soft_skills": [
    {"skill": "skill name", "evidence": "quote or signal from JD"}
  ],
  "red_flags": [
    {"flag": "description of concern", "severity": "low/medium/high"}
  ],
  "culture_signals": ["signal 1", "signal 2"],
  "interview_topics": ["topic 1", "topic 2", "topic 3"],
  "questions_to_ask": ["question 1", "question 2"]
}
---JSON_DATA_END---
```

---

## 5. API ENDPOINTS

### POST `/api/analyze-job`

**Rate Limit:** 20/hour

**Request Body:**
```typescript
{
  job_description: string,  // min 10, max 50000 chars
  mode: 'quick' | 'standard' | 'deep' | 'max',
  interviewer_type: 'hr' | 'technical' | 'manager' | 'general',
  provider: 'claude' | 'gemini',
  token?: string  // optional auth token
}
```

**Response:**
```typescript
{
  analysis: string,  // markdown report
  mode: string
}
```

### GET `/api/xray/analyses`

Lists user's previous X-Ray analyses for Smart Questions selection.

**Query Params:** `token` (required)

**Response:**
```typescript
{
  analyses: Array<{
    id: string,
    job_title: string,
    company_name?: string,
    created_at: string
  }>
}
```

---

## 6. DATA FLOW

1. User enters job description in `UnderstandJobPage.tsx`
2. User selects interviewer type (HR/Technical/Manager/General)
3. User selects depth level (Interview Ready / Fully Prepared)
4. User selects AI provider (Claude/Gemini)
5. Frontend calls `POST /api/analyze-job`
6. Backend (`analyze.py`) fetches prompts from `prompt_templates` table (or uses fallbacks)
7. Backend calls AI service (`ai_service.py`) via LiteLLM
8. AI response is parsed: markdown report + structured JSON
9. Results saved to `job_descriptions` and `xray_analyses` tables
10. Markdown report returned to frontend
11. Frontend renders with ReactMarkdown + remark-gfm

---

## 7. PROMPT ASSEMBLY LOGIC

The `get_combined_prompt()` function in `analyze.py`:

1. Tries to fetch `system_v2` prompt from DB
2. Tries to fetch `interviewer_{type}` prompt from DB
3. Tries to fetch `depth_{level}` prompt from DB
4. Falls back to hardcoded prompts if DB returns empty
5. Appends `JSON_STRUCTURE_SUFFIX` to depth prompt if not present
6. Combines: `system + interviewer + depth`

---

**END OF DOCUMENTATION**
