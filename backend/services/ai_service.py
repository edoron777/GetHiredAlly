import os
import logging
import time
from typing import Optional, Literal
from dataclasses import dataclass
import litellm
from supabase import create_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

litellm.drop_params = True

def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return create_client(url, key)
    return None

async def log_ai_usage(
    user_id: Optional[str],
    service_name: str,
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    cost_usd: Optional[float],
    duration_ms: int,
    success: bool,
    error_message: Optional[str] = None
):
    """Log AI usage to the database for tracking and billing."""
    try:
        supabase = get_supabase()
        if not supabase:
            logger.warning("Supabase not configured, skipping AI usage logging")
            return
        
        log_entry = {
            "user_id": user_id,
            "service_name": service_name,
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost_usd": float(cost_usd) if cost_usd else None,
            "duration_ms": duration_ms,
            "success": success,
            "error_message": error_message
        }
        
        supabase.table("ai_usage_logs").insert(log_entry).execute()
        logger.info(f"Logged AI usage: {service_name}/{provider}, tokens: {total_tokens}, cost: ${cost_usd:.6f}" if cost_usd else f"Logged AI usage: {service_name}/{provider}, tokens: {total_tokens}")
    except Exception as e:
        logger.error(f"Failed to log AI usage: {str(e)}")

@dataclass
class AIResponse:
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    provider: str
    cost: Optional[float] = None

PROVIDER_MODELS = {
    'claude': 'anthropic/claude-sonnet-4-5',
    'gemini': 'gemini/gemini-2.5-pro-preview-05-06',
}

async def generate_completion(
    prompt: str,
    system_prompt: Optional[str] = None,
    provider: Literal['claude', 'gemini'] = 'claude',
    max_tokens: int = 4096,
    temperature: float = 0.7,
    user_id: Optional[str] = None,
    service_name: str = "unknown"
) -> AIResponse:
    """
    Unified AI completion function that routes to any provider via LiteLLM.
    Automatically logs usage to the database.
    
    Args:
        prompt: The user message/prompt
        system_prompt: Optional system message
        provider: 'claude' or 'gemini'
        max_tokens: Maximum tokens for response
        temperature: Temperature for generation
        user_id: Optional user ID for usage tracking
        service_name: Service name for logging (e.g., 'xray', 'smart_questions')
        
    Returns:
        AIResponse with content, token counts, and cost
    """
    model = PROVIDER_MODELS.get(provider)
    if not model:
        raise ValueError(f"Unknown provider: {provider}. Use 'claude' or 'gemini'")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    logger.info(f"Calling {provider} ({model}) with {len(prompt)} char prompt")
    
    start_time = time.time()
    
    try:
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        content = response.choices[0].message.content or ""
        usage = response.usage
        
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0
        
        cost = None
        try:
            cost = litellm.completion_cost(completion_response=response)
        except Exception:
            pass
        
        logger.info(f"Response: {output_tokens} tokens, cost: ${cost:.4f}, duration: {duration_ms}ms" if cost else f"Response: {output_tokens} tokens, duration: {duration_ms}ms")
        
        await log_ai_usage(
            user_id=user_id,
            service_name=service_name,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            duration_ms=duration_ms,
            success=True
        )
        
        return AIResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            model=model,
            provider=provider,
            cost=cost
        )
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"AI generation failed with {provider}: {str(e)}")
        
        await log_ai_usage(
            user_id=user_id,
            service_name=service_name,
            provider=provider,
            model=model,
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            cost_usd=None,
            duration_ms=duration_ms,
            success=False,
            error_message=str(e)
        )
        
        raise

def generate_completion_sync(
    prompt: str,
    system_prompt: Optional[str] = None,
    provider: Literal['claude', 'gemini'] = 'claude',
    max_tokens: int = 4096,
    temperature: float = 0.7
) -> AIResponse:
    """
    Synchronous version of generate_completion for non-async contexts.
    """
    model = PROVIDER_MODELS.get(provider)
    if not model:
        raise ValueError(f"Unknown provider: {provider}. Use 'claude' or 'gemini'")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    logger.info(f"Calling {provider} ({model}) with {len(prompt)} char prompt")
    
    try:
        response = litellm.completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        content = response.choices[0].message.content or ""
        usage = response.usage
        
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0
        
        cost = None
        try:
            cost = litellm.completion_cost(completion_response=response)
        except Exception:
            pass
        
        logger.info(f"Response: {output_tokens} tokens, cost: ${cost:.4f}" if cost else f"Response: {output_tokens} tokens")
        
        return AIResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            model=model,
            provider=provider,
            cost=cost
        )
        
    except Exception as e:
        logger.error(f"AI generation failed with {provider}: {str(e)}")
        raise
