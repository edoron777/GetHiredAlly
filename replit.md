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

## Frontend Routes
- `/` - Landing page
- `/register` - User registration
- `/login` - User login
- `/verify-email` - Email verification page
- `/dashboard` - Main dashboard with service cards (protected)
- `/service/understand-job` - X-Ray analyzer input form (protected)

## Database Tables
- `user_profiles` - User tier definitions (standard, special, vip)
- `profile_limits` - Usage limits per profile and service
- `users` - User accounts with password hashes
- `services` - Available services (xray, questions, playbook)
- `usage_tracking` - Track user usage per service
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

## Recent Changes
- December 26, 2025: Built X-Ray Analyzer input page with job description textarea, character count, 3 analysis mode cards, and form validation
- December 26, 2025: Added dashboard with 3 service cards, protected routes
- December 26, 2025: Added email verification with Resend API, 6-digit codes, and verification page
- December 26, 2025: Added user login/logout with session management, bcrypt password verification
- December 26, 2025: Added user registration with bcrypt password hashing, email validation, React form
- December 26, 2025: Created Supabase schema with 13 tables for user management and services
- December 25, 2025: Fixed deployment config - FastAPI now serves built frontend in production
- December 25, 2025: Transformed project to React+Vite+Tailwind+shadcn/ui frontend with FastAPI backend
