# MinAgent - Minimal LLM Agent Framework

A lightweight, minimal framework for building LLM agents with tool calling capabilities. Built on a simple flow-based architecture with just the essentials.

## Features

- **Minimal codebase** - Under 300 lines of core code
- **Dynamic tool calling** - Register any Python function as a tool
- **Conversation memory** - Maintains context across agent calls
- **YAML-based decisions** - Structured LLM outputs for reliability
- **Flexible LLM support** - Works with OpenAI and OpenRouter

## Installation

```bash
pip install minagent
```

## Quick Start

```python
from minagent import Agent, configure_llm

# Define tools
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Results for {query}..."

def calculate(expression: str) -> float:
    """Evaluate a math expression."""
    return eval(expression)

# Configure LLM (optional - defaults to OpenRouter)
configure_llm(api_key="your-api-key")

# Create agent
agent = Agent(
    base_prompt="You are a helpful assistant.",
    tools=[search_web, calculate]
)

# Use agent
response = agent("What is 2+2?")
print(response)
```

## How It Works

1. **Decision Node**: LLM decides whether to call a tool or provide final answer
2. **Tool Node**: Executes the selected tool with provided arguments  
3. **Answer Node**: Formats and returns the final response
4. **Flow Control**: Cycles between decision and tool nodes until answer is ready

## Architecture

```
minagent/
├── agent.py      # Main Agent class and interface
├── nodes.py      # Decision, Tool, and Answer nodes
├── flow.py       # Flow orchestration
└── utils.py      # LLM utilities
```

## API

### Agent Class

```python
Agent(base_prompt: str, tools: list)
```

- `base_prompt`: System prompt defining agent behavior
- `tools`: List of callable functions with docstrings

### Configure LLM

```python
configure_llm(provider='openrouter', api_key=None, model=None, client=None)
```

- `provider`: 'openai' or 'openrouter' (default)
- `api_key`: API key for the provider
- `model`: Model to use (default: claude-3.5-sonnet)
- `client`: OpenAI client instance (for OpenAI provider)

## License

MIT 