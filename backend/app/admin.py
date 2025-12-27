from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/api/admin", tags=["admin"])

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
