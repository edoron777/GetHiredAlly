# GetHiredAlly - Interview Preparation Application

## Overview
GetHiredAlly is an interview preparation application with job description analysis ("X-Ray"), interview question preparation, and answer crafting features. Built with React frontend and FastAPI backend, connected to Supabase for data persistence.

## Tech Stack
- **Frontend**: React 19 with Vite, Tailwind CSS, shadcn/ui, React Router v7
- **Backend**: FastAPI (Python) with bcrypt for password hashing
- **Database**: Supabase (PostgreSQL)

## Brand Colors
- Background: #FAF9F7 (warm beige)
- Primary: #1E3A5F (navy blue)
- Text: #333333

## Project Structure
```
/
├── client/               # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   │   ├── ui/       # shadcn/ui components (Button, Input, Label)
│   │   │   ├── LandingPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   └── LoginPage.tsx
│   │   ├── lib/          # Utility functions (utils.ts, auth.ts)
│   │   ├── App.tsx       # Main app with routing
│   │   └── main.tsx      # Entry point
│   ├── dist/             # Built frontend (production)
│   └── vite.config.ts    # Vite configuration
├── backend/              # FastAPI backend
│   └── app/
│       ├── main.py       # API endpoints + static file serving
│       └── auth.py       # Authentication endpoints
├── supabase_schema.sql   # Database schema for Supabase
└── replit.md             # This file
```

## Development
- Frontend dev server runs on port 5000 (Vite with HMR)
- Backend runs on port 8000 (with auto-reload)
- Frontend proxies `/api/*` requests to the backend

## Production/Deployment
- Build: `cd client && npm run build` (creates dist/ folder)
- Run: FastAPI serves both API and static frontend on port 5000
- The backend serves the built React app and handles SPA routing

## Environment Variables
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key

## API Endpoints
- `GET /api/health` - Health check endpoint
- `GET /api/config` - Get configuration info
- `GET /api/supabase-test` - Test Supabase connection
- `POST /api/auth/register` - User registration (name, email, password)
- `POST /api/auth/login` - User login (email, password) - returns token and user data
- `POST /api/auth/logout` - Logout (token) - invalidates session
- `GET /api/auth/me?token=...` - Get current user from session token
- `POST /api/auth/send-verification` - Send verification code email
- `POST /api/auth/verify-email` - Verify email with 6-digit code
- `POST /api/analyze-job` - Analyze job description with Claude AI (job_description, mode)
- `GET /api/questions/static` - Get 54 interview questions (filterable by category)
- `GET /api/questions/categories` - Get available question categories
- `POST /api/questions/seed?force=true` - Seed interview questions to database (force replaces all)
- `GET /api/xray/analyses?token=...` - List user's X-Ray analyses for dropdown
- `GET /api/smart-questions/check-eligibility?token=...` - Check if user can use Smart Questions
- `POST /api/smart-questions/generate` - Generate personalized questions with Gemini AI
- `GET /api/smart-questions/{id}?token=...` - Get a specific smart questions result
- `GET /api/smart-questions/?token=...` - List user's smart question results

## Frontend Routes
- `/` - Landing page
- `/service/cv-optimizer` - CV Optimizer placeholder page (protected)
- `/register` - User registration
- `/login` - User login
- `/verify-email` - Email verification page
- `/dashboard` - Main dashboard with service cards (protected)
- `/service/understand-job` - X-Ray analyzer input form (protected)
- `/service/predict-questions` - Questions service home with 2 cards (protected)
- `/service/predict-questions/common` - 54 common interview questions (protected)
- `/service/predict-questions/smart` - Smart Questions AI input page (protected)
- `/service/predict-questions/smart/results/:id` - Smart Questions results page (protected)

## Database Tables
- `user_profiles` - User tier definitions (standard, special, vip)
- `profile_limits` - Usage limits per profile and service
- `users` - User accounts with password hashes (includes smart_questions_free_used flag)
- `services` - Available services (xray, questions, playbook)
- `usage_tracking` - Track user usage per service
- `smart_question_results` - AI-generated personalized interview questions (stores weak_areas and personalized_questions as JSONB)
- `ai_usage_logs` - Tracks every AI API call (provider, tokens, cost, duration)
- `user_ai_preferences` - User preferences for AI providers per service
- See `supabase_schema.sql` for complete schema

## User Profiles
- **Standard**: 1 xray/week, 5 static questions total, 1 dynamic question/week
- **Special**: 3 xray/week, 5 static questions total, 3 dynamic questions/week
- **VIP**: 20 xray/week, unlimited static questions, 20 dynamic questions/week

## Session Management
- Sessions stored in `user_sessions` table with hashed tokens
- Tokens expire after 7 days
- Client stores token in localStorage via `lib/auth.ts` utilities

## Email Verification
- Uses Resend API for sending verification emails
- 6-digit verification codes with 15-minute expiry
- Codes stored in `email_verification_codes` table
- **Note**: Resend free tier only sends to owner email (edoron777@gmail.com). Verify a domain at resend.com/domains to send to other addresses.

## Interview Questions Structure
- 54 questions organized into 5 categories: Universal (12), Behavioral (18), Situational (8), Self-Assessment (8), Cultural Fit (8)
- Each question has: question_text, why_they_ask, framework, good_answer_example, what_to_avoid
- 11 "Questions to Ask the Interviewer" with: why_ask, what_to_listen_for, warning_signs
- Depth levels control display only: questions_only (just questions), with_tips (+ why + framework), full_prep (+ good example + what to avoid)

## AI Service Architecture
- Unified AI service (`backend/services/ai_service.py`) routes to Claude or Gemini via LiteLLM
- AIProviderSelector component allows users to choose Claude (~$0.02) or Gemini (~$0.01)
- **Automatic Usage Logging**: Every AI call logs to `ai_usage_logs` table with:
  - user_id, service_name (xray/smart_questions), provider, model
  - input_tokens, output_tokens, total_tokens
  - cost_usd (calculated by LiteLLM's built-in cost tracking)
  - duration_ms, success/failure, error_message

## Smart Questions UX Design
- Uses supportive coaching-style language instead of warning-style
- Focus Areas (not "weak areas") with priority levels:
  - KEY_FOCUS (blue) - Most important areas to prepare
  - WORTH_PREPARING (purple) - Helpful to practice
  - GOOD_TO_KNOW (gray) - Nice to have
- Each focus area includes coaching tips and winning approaches
- Introduction section with encouraging preparation message
- Backward compatible with legacy data (weak_areas → focus_areas mapping)

## Security Implementation
- **Security Headers Middleware**: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, HSTS, Referrer-Policy, Permissions-Policy
- **Rate Limiting**: Login 5/min, Register 10/hr, AI calls 10-20/hr
- **Audit Logging**: Login attempts, security events logged to `backend/logs/audit.log`
- **CV Encryption**: CV text encrypted at rest using Fernet (ENCRYPTION_KEY secret required)
- **Input Validation**: Pydantic models for all API inputs with sanitization
- **Password Security**: bcrypt hashing, passwords never logged

## Recent Changes
- December 27, 2025: Built CV scanning animation page with grid visualization, progress bar, and issue counters
- December 27, 2025: Added AI-powered CV analysis using Gemini with detailed issue detection (severity, category, suggestions)
- December 27, 2025: Created CV results page showing all issues with severity badges and fix suggestions
- December 27, 2025: Built CV upload page with drag & drop, file validation, and backend API for text extraction
- December 27, 2025: Added user_cvs table and CV management endpoints (/api/cv/list, /api/cv/upload-for-scan)
- December 27, 2025: Added CV Optimizer service card to dashboard and cv_scan_results database table
- December 27, 2025: Added security headers middleware and audit logging for login/security events
- December 27, 2025: Implemented CV encryption at rest with Fernet cryptography
- December 27, 2025: Added rate limiting to sensitive API endpoints
- December 27, 2025: Display level buttons now one-line horizontal with colored icons (blue List, yellow Lightbulb, purple BookOpen, gold Star)
- December 27, 2025: Added Filter icon on title line, removed sublabels for cleaner compact design
- December 27, 2025: Navy blue StandardToolbar with Expand/Collapse, Email, WhatsApp, PDF, Word, and Markdown buttons
- December 27, 2025: Unified layout across Static and Smart Questionnaire pages with identical toolbar and section headers
- December 27, 2025: Added document footer with branding (GetHiredAlly | service_name | gethiredally.com) to PDF/Word downloads
- December 27, 2025: Updated Smart Questions UX with coaching-style language and supportive design (focus_areas, priority_levels, blue/purple colors)
- December 27, 2025: Changed Gemini model to gemini-2.0-flash (1.5 models retired)
- December 27, 2025: Added automatic AI usage logging with LiteLLM cost tracking to ai_usage_logs table
- December 27, 2025: Added AIProviderSelector component to X-Ray and Smart Questions pages
- December 27, 2025: Expanded to 54 interview questions with new structure (good_answer_example, what_to_avoid fields)
- December 27, 2025: Removed interviewer type filter, simplified to category-only filtering
- December 27, 2025: Added question_categories table with category descriptions and answer methods
- December 26, 2025: Built Interview Questions Predictor UI page with depth level selectors (Questions Only, With Tips, Full Prep), expandable question cards, and PDF/Word download
- December 26, 2025: Added Interview Questions Predictor backend - API endpoints with filtering
- December 26, 2025: Enhanced X-Ray analysis with structured JSON output, table of contents, callout boxes (red flags, insights, strengths, tips), and Next Step CTA
- December 26, 2025: Added job_descriptions and xray_analyses tables for storing analysis results
- December 26, 2025: Added Claude API integration for job description analysis with 3 modes (quick, deep, max)
- December 26, 2025: Built X-Ray Analyzer input page with job description textarea, character count, 3 analysis mode cards, and form validation
- December 26, 2025: Added dashboard with 3 service cards, protected routes
- December 26, 2025: Added email verification with Resend API, 6-digit codes, and verification page
- December 26, 2025: Added user login/logout with session management, bcrypt password verification
- December 26, 2025: Added user registration with bcrypt password hashing, email validation, React form
- December 26, 2025: Created Supabase schema with 13 tables for user management and services
- December 25, 2025: Fixed deployment config - FastAPI now serves built frontend in production
- December 25, 2025: Transformed project to React+Vite+Tailwind+shadcn/ui frontend with FastAPI backend
