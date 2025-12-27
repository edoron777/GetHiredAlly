import os
import logging
from typing import Optional, Literal
from dataclasses import dataclass
import litellm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

litellm.drop_params = True

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
    temperature: float = 0.7
) -> AIResponse:
    """
    Unified AI completion function that routes to any provider via LiteLLM.
    
    Args:
        prompt: The user message/prompt
        system_prompt: Optional system message
        provider: 'claude' or 'gemini'
        max_tokens: Maximum tokens for response
        temperature: Temperature for generation
        
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
    
    try:
        response = await litellm.acompletion(
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
