import os

def call_llm_openai(prompt, client, model, params={}):    
    """Call OpenAI LLM without streaming."""
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        **params
    )
    return r.choices[0].message.content

def call_llm_openai_stream(prompt, client, model, params={}):
    """Call OpenAI LLM with streaming."""
    s = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        **params
    )
    
    for chunk in s:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

def call_llm_openrouter(api_key, prompt, model, params={}):
    """Call OpenRouter LLM without streaming."""
    import requests

    r = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            **params
        }
    )
    r = r.json()
    return r["choices"][0]["message"]["content"]

def call_llm_openrouter_stream(api_key, prompt, model, params={}):
    """Call OpenRouter LLM with streaming."""
    import requests
    import json

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        **params
    }

    with requests.post(url, headers=headers, json=payload, stream=True) as r:
        buffer = ""
        for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                buffer += chunk
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            return
                        
                        try:
                            data_obj = json.loads(data)
                            if "choices" in data_obj and len(data_obj["choices"]) > 0:
                                delta = data_obj["choices"][0].get("delta", {})
                                content = delta.get("content")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

# Default LLM configuration
_llm_config = {
    'provider': 'openrouter',
    'api_key': None,
    'model': 'anthropic/claude-3.5-sonnet',
    'client': None
}

def configure_llm(provider='openrouter', api_key=None, model=None, client=None):
    """Configure the default LLM for the framework.
    
    Args:
        provider: 'openai' or 'openrouter' 
        api_key: API key for the provider
        model: Model name to use
        client: OpenAI client instance (for OpenAI provider)
    """
    _llm_config['provider'] = provider
    if api_key:
        _llm_config['api_key'] = api_key
    if model:
        _llm_config['model'] = model
    if client:
        _llm_config['client'] = client

def call_llm(prompt, **params):
    """Call the configured LLM with the given prompt.
    
    Args:
        prompt: Text prompt for the LLM
        **params: Additional parameters for the LLM
        
    Returns:
        LLM response as string
    """
    provider = _llm_config['provider']
    
    try:
        if provider == 'openai':
            if not _llm_config['client']:
                raise ValueError("OpenAI client not configured. Use configure_llm()")
            response = call_llm_openai(
                prompt, 
                _llm_config['client'], 
                _llm_config['model'],
                params
            )
        elif provider == 'openrouter':
            api_key = _llm_config['api_key'] or os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                raise ValueError("OpenRouter API key not configured")
            response = call_llm_openrouter(
                api_key,
                prompt,
                _llm_config['model'],
                params
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        return response
        
    except Exception as e:
        from .logger import get_logger
        logger = get_logger()
        logger.error(f"LLM call failed: {str(e)}")
        raise