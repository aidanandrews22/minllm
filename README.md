# MinLLM - Ultra-Lightweight Workflow Framework

A blazingly fast, zero-dependency framework for building directed graphs, LLM workflows, and agent systems. Written in an astonishingly minimal amount of code (~100 lines) while maintaining full expressiveness through operator overloading.

## 🚀 Key Features

- **Zero Dependencies** - Pure Python, no external packages required
- **Ultra-Lightweight** - Core framework in just ~100 lines of code
- **Expressive Syntax** - Unique operator-based flow construction (`>>`, `-`)
- **Async/Sync Support** - Full async/await support with parallel execution
- **Developer-First** - Code-centric design, no YAML/JSON configuration
- **Production Ready** - Built-in retry logic, error handling, and batching

## 🏗️ Architecture

MinLLM provides a simple yet powerful abstraction for building workflows:

```
BaseNode → Node → Flow
    ↓        ↓      ↓
AsyncNode → AsyncFlow → AsyncBatchFlow
```

### Core Components

- **Nodes** - Individual processing units with `prep()`, `exec()`, `post()` lifecycle
- **Flows** - Orchestrate node execution with conditional branching
- **Batch Processing** - Handle collections with `BatchNode` and `BatchFlow`
- **Async Support** - Full async/await with parallel execution capabilities

## 📦 What's Included

### Core Framework (`__init__.py`)
- `BaseNode` - Foundation for all processing units
- `Node` - Synchronous node with retry logic
- `Flow` - Orchestrates node execution with branching
- `AsyncNode` - Asynchronous processing with parallel support
- `BatchNode` - Process collections efficiently

### MinAgent Subframework (`minagent/`)
A complete LLM agent framework built on MinLLM:
- Dynamic tool calling
- Conversation memory
- YAML-structured decisions
- OpenAI/OpenRouter support

## 🔥 Expressive Syntax

MinLLM's operator overloading creates incredibly readable workflows:

```python
from minllm import Node, Flow

# Create nodes
validate = Node()
process = Node() 
save = Node()
notify = Node()

# Build flow with operators
flow = Flow(start=validate)
validate >> process >> save
validate - "error" >> notify

# Run workflow
result = flow.run(shared_data)
```

## 🚀 Quick Examples

### Basic Node

```python
from minllm import Node

class ProcessData(Node):
    def prep(self, shared):
        return shared.get('input_data')
    
    def exec(self, prep_res):
        return prep_res.upper()
    
    def post(self, shared, prep_res, exec_res):
        shared['result'] = exec_res
        return exec_res

# Use it
node = ProcessData()
result = node.run({'input_data': 'hello world'})
```

### Conditional Flow

```python
from minllm import Node, Flow

class Validator(Node):
    def exec(self, data):
        return "valid" if data.get('email') else "invalid"

class SendEmail(Node):
    def exec(self, data):
        return f"Email sent to {data['email']}"

class LogError(Node):
    def exec(self, data):
        return "Invalid email logged"

# Build conditional flow
validator = Validator()
send_email = SendEmail()
log_error = LogError()

flow = Flow(start=validator)
validator - "valid" >> send_email
validator - "invalid" >> log_error

# Execute
result = flow.run({'email': 'user@example.com'})
```

### Async Parallel Processing

```python
from minllm import AsyncParallelBatchNode
import asyncio

class FetchData(AsyncParallelBatchNode):
    async def exec_async(self, url):
        # Simulate API call
        await asyncio.sleep(0.1)
        return f"Data from {url}"

# Process URLs in parallel
fetcher = FetchData()
urls = ['api1.com', 'api2.com', 'api3.com']
results = await fetcher.run_async(urls)
```

### Retry Logic

```python
from minllm import Node

class APICall(Node):
    def __init__(self):
        super().__init__(max_retries=3, wait=1)
    
    def exec(self, endpoint):
        # This will retry up to 3 times with 1s wait
        return make_api_call(endpoint)
    
    def exec_fallback(self, prep_res, exc):
        return {"error": str(exc), "endpoint": prep_res}
```

## 🤖 MinAgent - LLM Agent Framework

Built on MinLLM, MinAgent provides a complete agent framework:

```python
from minagent import Agent, configure_llm

def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Results for {query}..."

configure_llm(api_key="your-key")

agent = Agent(
    base_prompt="You are a helpful assistant.",
    tools=[search_web]
)

response = agent("What's the weather like?")
```

## 🎯 Why MinLLM?

### vs. LangChain
- **100x smaller** - 100 lines vs 10,000+ lines
- **Zero dependencies** - No dependency hell
- **Faster execution** - Minimal overhead
- **Clearer syntax** - Operator-based flow construction

### vs. Custom Solutions
- **Battle-tested patterns** - Retry, batching, async built-in
- **Expressive syntax** - Readable workflow construction
- **Production ready** - Error handling and logging

### vs. Workflow Engines
- **Lightweight** - No infrastructure requirements
- **Code-first** - No YAML/JSON configuration
- **Python native** - Leverage full Python ecosystem

## 📋 Node Lifecycle

Every node follows a consistent 3-phase lifecycle:

1. **`prep(shared)`** - Prepare data from shared context
2. **`exec(prep_res)`** - Execute core logic with prepared data
3. **`post(shared, prep_res, exec_res)`** - Post-process and update shared context

## 🔄 Flow Control

Flows orchestrate node execution with powerful branching:

```python
# Default transition
node1 >> node2

# Conditional transitions
node1 - "success" >> node2
node1 - "error" >> error_handler

# Multiple conditions
validator - "valid" >> processor
validator - "invalid" >> error_logger
validator - "retry" >> validator  # Self-loop
```

## 📊 Batch Processing

Handle collections efficiently:

```python
from minllm import BatchNode, BatchFlow

class ProcessItem(BatchNode):
    def exec(self, item):
        return item * 2

# Process list of items
processor = ProcessItem()
results = processor.run([1, 2, 3, 4, 5])  # [2, 4, 6, 8, 10]
```

## ⚡ Async & Parallel

Full async support with parallel execution:

```python
from minllm import AsyncParallelBatchFlow

# Process items in parallel
flow = AsyncParallelBatchFlow(start=async_processor)
results = await flow.run_async(large_dataset)
```

## 🛠️ Installation

```bash
# Core framework (zero dependencies)
pip install minllm

# With agent capabilities
pip install minllm[agent]
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🎯 Philosophy

MinLLM embodies the principle that **powerful doesn't mean complex**. By focusing on essential patterns and leveraging Python's expressiveness, we've created a framework that's both incredibly lightweight and surprisingly capable.

Perfect for developers who want:
- **Control** over their workflows
- **Performance** without bloat  
- **Expressiveness** without complexity
- **Reliability** without dependencies
