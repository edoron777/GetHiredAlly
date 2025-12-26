import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from supabase import create_client, Client
from app.auth import router as auth_router

app = FastAPI(title="Backend API")
app.include_router(auth_router)

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

static_dir = Path(__file__).parent.parent.parent / "client" / "dist"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(static_dir / "index.html")
