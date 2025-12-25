# Full-Stack React + FastAPI Application

## Overview
A full-stack web application with React frontend and FastAPI backend, connected to Supabase.

## Tech Stack
- **Frontend**: React with Vite, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)

## Project Structure
```
/
├── client/               # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   │   └── ui/       # shadcn/ui components
│   │   ├── lib/          # Utility functions
│   │   ├── App.tsx       # Main app component
│   │   └── main.tsx      # Entry point
│   └── vite.config.ts    # Vite configuration
├── backend/              # FastAPI backend
│   └── app/
│       └── main.py       # API endpoints
└── replit.md             # This file
```

## Running the Application
- Frontend runs on port 5000 (exposed to web)
- Backend runs on port 8000 (internal API)
- Frontend proxies `/api/*` requests to the backend

## Environment Variables
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key

## API Endpoints
- `GET /api/health` - Health check endpoint
- `GET /api/config` - Get configuration info

## Recent Changes
- December 25, 2025: Transformed project to React+Vite+Tailwind+shadcn/ui frontend with FastAPI backend
