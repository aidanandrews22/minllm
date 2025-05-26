from .flow import create_agent_flow
from .nodes import DecideAction, CallTool, ProvideAnswer
from .logger import set_logging, get_logger
import inspect
from typing import get_type_hints

class Agent:
    def __init__(self, base_prompt, tools=None, logging=False, verbose_logging=False):
        """Initialize agent with base prompt and available tools.
        
        Args:
            base_prompt: System prompt defining agent behavior
            tools: List of callable functions to use as tools
            logging: Enable basic logging
            verbose_logging: Enable verbose logging (includes basic logging)
        """
        # Configure global logging
        set_logging(enabled=logging or verbose_logging, verbose=verbose_logging)
        self.logger = get_logger()
        self.base_prompt = base_prompt
        self.tools = tools or []
        self.conversation_history = []
        self.tool_call_history = []
        
        self.tool_registry = {}
        for tool in self.tools:
            tool_info = self.register_tool(tool)
            self.tool_registry[tool_info['name']] = tool_info

    def register_tool(self, tool):
        """Extract metadata from a callable tool."""
        name = tool.__name__
        sig = inspect.signature(tool)
        type_hints = get_type_hints(tool)
        doc = inspect.getdoc(tool) or f"Function {name}"

        params = {}
        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name, 'Any')
            default = (
                param.default
                if param.default is not inspect.Parameter.empty
                else None
            )

            params[param_name] = {
                'type': str(param_type),
                'default': default,
                'kind': str(param.kind),
            }

        return {
            'name': name,
            'function': tool,
            'description': doc,
            'parameters': params
        }

    
    def __call__(self, query):
        """Execute agent on a query."""
        return self.run(query)
    
    def run(self, query):
        """Run agent on a query, managing context and history.
        
        Args:
            query: User question or request
            
        Returns:
            Agent's response after tool usage and reasoning
        """
        # Log agent start
        self.logger.agent_start(query)
        
        # Add query to conversation history
        self.conversation_history.append({'role': 'user', 'content': query})
        
        # Create flow with current tools
        flow = create_agent_flow(self.tool_registry)
        
        # Prepare shared context
        shared = {
            'query': query,
            'base_prompt': self.base_prompt,
            'conversation_history': self._get_optimized_history(),
            'tool_registry': self.tool_registry,
            'tool_calls': []
        }
        
        # Execute flow
        self.logger.verbose_log("Starting workflow execution")
        flow.run(shared)
        
        # Extract final answer
        answer = shared.get('final_answer', 'Unable to generate response')
        
        # Log final answer
        self.logger.final_answer(answer)
        
        # Update histories
        self.conversation_history.append({'role': 'assistant', 'content': answer})
        self.tool_call_history.extend(shared.get('tool_calls', []))
        
        return answer
    
    def _get_optimized_history(self):
        """Optimize conversation history to fit context limits."""
        # Keep last 10 exchanges (20 messages) for context
        recent_history = self.conversation_history[-20:]
        
        # Format as string for LLM context
        if not recent_history:
            return "No previous conversation"
        
        formatted = []
        for msg in recent_history:
            role = msg['role'].upper()
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)
    
    def clear_history(self):
        """Clear conversation and tool call history."""
        self.conversation_history = []
        self.tool_call_history = []