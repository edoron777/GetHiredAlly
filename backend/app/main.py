import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from supabase import create_client, Client
from slowapi.errors import RateLimitExceeded

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.rate_limiter import limiter, rate_limit_exceeded_handler
from middleware.security_headers import SecurityHeadersMiddleware

from .auth import router as auth_router
from .analyze import router as analyze_router
from .downloads import router as downloads_router
from .questions import router as questions_router
from .smart_questions import router as smart_questions_router
from .admin import router as admin_router
from .cv import router as cv_router
from .cv_optimizer import router as cv_optimizer_router
from .user import router as user_router
from common.catalog import init_catalog_service
from routes.catalog_routes import router as catalog_router

app = FastAPI(title="Backend API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(analyze_router)
app.include_router(downloads_router)
app.include_router(questions_router)
app.include_router(smart_questions_router)
app.include_router(admin_router)
app.include_router(cv_router)
app.include_router(cv_optimizer_router)
app.include_router(user_router)
app.include_router(catalog_router)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_supabase_client() -> Client | None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if url and key:
        return create_client(url, key)
    return None

try:
    supabase_client = get_supabase_client()
    if supabase_client:
        catalog_service = init_catalog_service(supabase_client)
        print("✓ CV Issue Catalog loaded successfully")
    else:
        print("⚠ Warning: Supabase not configured, catalog features unavailable")
except Exception as e:
    print(f"⚠ Warning: Failed to load CV Issue Catalog: {e}")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/config")
async def get_config():
    supabase_url = os.environ.get("SUPABASE_URL", "")
    return {
        "supabase_url": supabase_url,
        "has_supabase": bool(supabase_url)
    }

@app.get("/api/supabase-test")
async def test_supabase_connection():
    try:
        client = get_supabase_client()
        if not client:
            return {"connected": False, "error": "Missing SUPABASE_URL or SUPABASE_ANON_KEY"}
        
        try:
            result = client.table("user_profiles").select("profile_name").limit(3).execute()
            return {
                "connected": True,
                "supabase_url": os.environ.get("SUPABASE_URL", ""),
                "tables_exist": True,
                "profiles_found": len(result.data),
                "profiles": [p["profile_name"] for p in result.data]
            }
        except Exception as table_error:
            return {
                "connected": True,
                "supabase_url": os.environ.get("SUPABASE_URL", ""),
                "tables_exist": False,
                "note": "Connection works but tables need to be created in Supabase dashboard",
                "table_error": str(table_error)
            }
    except Exception as e:
        return {"connected": False, "error": str(e)}

possible_static_dirs = [
    Path(__file__).parent.parent.parent / "client" / "dist",
    Path("/home/runner/workspace/client/dist"),
    Path("client/dist"),
    Path("./client/dist"),
]

static_dir = None
for candidate in possible_static_dirs:
    if candidate.exists() and (candidate / "index.html").exists():
        static_dir = candidate
        print(f"✓ Static files found at: {static_dir}")
        break

if static_dir:
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            return {"error": "Not found"}
        file_path = static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(static_dir / "index.html")
else:
    print("⚠ Warning: Static files not found, frontend will not be served")
