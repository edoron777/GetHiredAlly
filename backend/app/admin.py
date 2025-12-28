from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/api/admin", tags=["admin"])

PROTECTED_ADMIN_EMAIL = "edoron777+admin@gmail.com"


class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_admin: Optional[bool] = None
    is_verified: Optional[bool] = None
    profile_id: Optional[str] = None

def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=500, detail="Database not configured")
    return psycopg2.connect(database_url)


@router.get("/ai-usage/summary")
async def get_ai_usage_summary(days: int = Query(default=30, ge=1, le=365)):
    """Get summary statistics for AI usage"""
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT * FROM ai_usage_logs WHERE created_at >= %s",
            (cutoff_date,)
        )
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        total_requests = len(logs)
        successful = sum(1 for l in logs if l.get("success", False))
        success_rate = (successful / total_requests * 100) if total_requests > 0 else 0
        total_cost = sum(float(l.get("cost_usd") or 0) for l in logs)
        total_tokens = sum(int(l.get("total_tokens") or 0) for l in logs)
        avg_duration = sum(int(l.get("duration_ms") or 0) for l in logs) / total_requests if total_requests > 0 else 0
        
        cost_by_provider = {}
        requests_by_provider = {}
        for log in logs:
            provider = log.get("provider", "unknown")
            cost_by_provider[provider] = cost_by_provider.get(provider, 0) + float(log.get("cost_usd") or 0)
            requests_by_provider[provider] = requests_by_provider.get(provider, 0) + 1
        
        cost_by_service = {}
        requests_by_service = {}
        for log in logs:
            service = log.get("service_name", "unknown")
            cost_by_service[service] = cost_by_service.get(service, 0) + float(log.get("cost_usd") or 0)
            requests_by_service[service] = requests_by_service.get(service, 0) + 1
        
        daily_data = {}
        for log in logs:
            created_at = log.get("created_at", "")
            if created_at:
                day = created_at[:10]
                if day not in daily_data:
                    daily_data[day] = {"cost": 0, "requests": 0, "tokens": 0}
                daily_data[day]["cost"] += float(log.get("cost_usd") or 0)
                daily_data[day]["requests"] += 1
                daily_data[day]["tokens"] += int(log.get("total_tokens") or 0)
        
        daily_trend = [
            {"date": k, "cost": round(v["cost"], 4), "requests": v["requests"], "tokens": v["tokens"]}
            for k, v in sorted(daily_data.items())
        ]
        
        return {
            "period_days": days,
            "summary": {
                "total_requests": total_requests,
                "successful_requests": successful,
                "success_rate": round(success_rate, 1),
                "total_cost": round(total_cost, 4),
                "total_tokens": total_tokens,
                "avg_duration_ms": round(avg_duration, 0)
            },
            "cost_by_provider": [{"provider": k, "cost": round(v, 4)} for k, v in cost_by_provider.items()],
            "requests_by_provider": [{"provider": k, "count": v} for k, v in requests_by_provider.items()],
            "cost_by_service": [{"service": k, "cost": round(v, 4)} for k, v in cost_by_service.items()],
            "requests_by_service": [{"service": k, "count": v} for k, v in requests_by_service.items()],
            "daily_trend": daily_trend
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch AI usage summary: {str(e)}")


@router.get("/ai-usage/recent")
async def get_recent_ai_calls(limit: int = Query(default=50, ge=1, le=200)):
    """Get recent AI API calls"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT id, user_id, service_name, provider, model, input_tokens, output_tokens, 
               total_tokens, cost_usd, duration_ms, success, error_message, created_at 
               FROM ai_usage_logs ORDER BY created_at DESC LIMIT %s""",
            (limit,)
        )
        calls = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for call in calls:
            if call.get('created_at'):
                call['created_at'] = call['created_at'].isoformat()
            if call.get('id'):
                call['id'] = str(call['id'])
            if call.get('user_id'):
                call['user_id'] = str(call['user_id'])
            if call.get('cost_usd'):
                call['cost_usd'] = float(call['cost_usd'])
        
        return {"calls": calls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent calls: {str(e)}")


@router.get("/ai-usage/by-user")
async def get_usage_by_user(days: int = Query(default=30, ge=1, le=365), limit: int = Query(default=20, ge=1, le=100)):
    """Get AI usage breakdown by user"""
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """SELECT 
                l.user_id,
                u.email,
                COUNT(*) as total_requests,
                COALESCE(SUM(l.cost_usd), 0) as total_cost,
                COALESCE(SUM(l.input_tokens), 0) as total_input_tokens,
                COALESCE(SUM(l.output_tokens), 0) as total_output_tokens,
                MAX(l.created_at) as last_used
            FROM ai_usage_logs l
            LEFT JOIN users u ON l.user_id = u.id
            WHERE l.created_at >= %s
            GROUP BY l.user_id, u.email
            ORDER BY total_cost DESC
            LIMIT %s""",
            (cutoff_date, limit)
        )
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for user in users:
            if user.get('user_id'):
                user['user_id'] = str(user['user_id'])
            if user.get('last_used'):
                user['last_used'] = user['last_used'].isoformat()
            if user.get('total_cost'):
                user['total_cost'] = float(user['total_cost'])
            if user.get('total_input_tokens'):
                user['total_input_tokens'] = int(user['total_input_tokens'])
            if user.get('total_output_tokens'):
                user['total_output_tokens'] = int(user['total_output_tokens'])
        
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user usage: {str(e)}")


@router.get("/stats")
async def get_admin_stats():
    """Get overview statistics for admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE created_at >= %s", (week_ago,))
        new_users_this_week = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_verified = TRUE")
        verified_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_admin = TRUE")
        admin_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM ai_usage_logs")
        total_ai_calls = cursor.fetchone()['count']
        
        cursor.execute("SELECT COALESCE(SUM(cost_usd), 0) as total FROM ai_usage_logs")
        total_ai_cost = float(cursor.fetchone()['total'] or 0)
        
        cursor.execute(
            """SELECT id, email, name, is_verified, created_at 
               FROM users ORDER BY created_at DESC LIMIT 10"""
        )
        recent_signups = cursor.fetchall()
        
        for user in recent_signups:
            if user.get('id'):
                user['id'] = str(user['id'])
            if user.get('created_at'):
                user['created_at'] = user['created_at'].isoformat()
        
        cursor.close()
        conn.close()
        
        return {
            "total_users": total_users,
            "new_users_this_week": new_users_this_week,
            "verified_users": verified_users,
            "admin_users": admin_users,
            "total_ai_calls": total_ai_calls,
            "total_ai_cost": round(total_ai_cost, 4),
            "recent_signups": recent_signups
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch admin stats: {str(e)}")


@router.get("/users")
async def get_all_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None)
):
    """Get paginated list of all users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        offset = (page - 1) * limit
        
        if search:
            search_pattern = f"%{search}%"
            cursor.execute(
                """SELECT COUNT(*) as count FROM users 
                   WHERE email ILIKE %s OR name ILIKE %s""",
                (search_pattern, search_pattern)
            )
            total = cursor.fetchone()['count']
            
            cursor.execute(
                """SELECT id, email, name, role, profile_id, is_admin, is_verified, google_id, created_at
                   FROM users 
                   WHERE email ILIKE %s OR name ILIKE %s
                   ORDER BY created_at DESC
                   LIMIT %s OFFSET %s""",
                (search_pattern, search_pattern, limit, offset)
            )
        else:
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total = cursor.fetchone()['count']
            
            cursor.execute(
                """SELECT id, email, name, role, profile_id, is_admin, is_verified, google_id, created_at
                   FROM users 
                   ORDER BY created_at DESC
                   LIMIT %s OFFSET %s""",
                (limit, offset)
            )
        
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for user in users:
            if user.get('id'):
                user['id'] = str(user['id'])
            if user.get('created_at'):
                user['created_at'] = user['created_at'].isoformat()
        
        total_pages = (total + limit - 1) // limit
        
        return {
            "users": users,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")


@router.put("/users/{user_id}")
async def update_user(user_id: str, data: UserUpdate):
    """Update user role, is_admin, is_verified, profile_id"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT email, is_admin FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        if user['email'] == PROTECTED_ADMIN_EMAIL:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=403, detail="Cannot modify protected admin account")
        
        updates = []
        values = []
        
        if data.role is not None:
            updates.append("role = %s")
            values.append(data.role)
        
        if data.is_admin is not None:
            updates.append("is_admin = %s")
            values.append(data.is_admin)
        
        if data.is_verified is not None:
            updates.append("is_verified = %s")
            values.append(data.is_verified)
        
        if data.profile_id is not None:
            updates.append("profile_id = %s")
            values.append(data.profile_id)
        
        if updates:
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, tuple(values))
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"message": "User updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user account"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        if user['email'] == PROTECTED_ADMIN_EMAIL:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=403, detail="Cannot delete protected admin account")
        
        cursor.execute("DELETE FROM cv_scans WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM ai_usage_logs WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM audit_logs WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM sessions WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
