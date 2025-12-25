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
│   ├── dist/             # Built frontend (production)
│   └── vite.config.ts    # Vite configuration
├── backend/              # FastAPI backend
│   └── app/
│       └── main.py       # API endpoints + static file serving
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

## Recent Changes
- December 25, 2025: Fixed deployment config - FastAPI now serves built frontend in production
- December 25, 2025: Transformed project to React+Vite+Tailwind+shadcn/ui frontend with FastAPI backend
