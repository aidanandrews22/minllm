from minllm import Node
from .utils import call_llm
from .logger import get_logger
import yaml
import json

class DecideAction(Node):
    def prep(self, shared):
        """Prepare context for decision-making."""
        logger = get_logger()
        logger.workflow_step("DecideAction.prep", "Preparing decision context")
        
        return {
            'query': shared['query'],
            'base_prompt': shared['base_prompt'],
            'conversation_history': shared['conversation_history'],
            'tool_registry': shared['tool_registry'],
            'tool_calls': shared['tool_calls']
        }
        
    def exec(self, inputs):
        """Decide next action: call a tool or provide final answer."""
        logger = get_logger()
        logger.workflow_step("DecideAction.exec", "Making decision")
        
        # Build tool descriptions
        tools_desc = []
        for name, info in inputs['tool_registry'].items():
            params_desc = []
            for param_name, param_info in info.get('parameters', {}).items():
                param_type = param_info['type']
                default = param_info.get('default')
                param_str = f"{param_name}: {param_type}"
                if default is not None:
                    param_str += f" = {default}"
                params_desc.append(param_str)
            
            params_text = f"({', '.join(params_desc)})" if params_desc else "()"
            tools_desc.append(f"- {name}{params_text}: {info['description']}")
        tools_text = "\n".join(tools_desc) if tools_desc else "No tools available"
        
        # Build previous tool calls summary
        tool_history = ""
        if inputs['tool_calls']:
            calls = []
            for call in inputs['tool_calls'][-5:]:  # Last 5 tool calls
                calls.append(f"- {call['tool']}: {call['result'][:200]}...")
            tool_history = "\nRecent Tool Calls:\n" + "\n".join(calls)
        
        prompt = f"""### SYSTEM
{inputs['base_prompt']}

### CONVERSATION HISTORY
{inputs['conversation_history']}

### CURRENT QUERY
{inputs['query']}

### AVAILABLE TOOLS
{tools_text}
{tool_history}

### DECISION
Decide the next action. You can either:
1. Call a tool to gather information
2. Provide the final answer if you have sufficient information

Return your decision in YAML format:

```yaml
thinking: |
    <step-by-step reasoning about what to do next>
action: tool OR answer
tool_name: <name of tool if action is tool>
tool_args: <arguments for tool as a dict if action is tool>
final_answer: |
    <complete answer if action is answer>
```
"""
        
        response = call_llm(prompt)
        
        # Log LLM call
        logger.llm_call(prompt, response)
        
        # Extract YAML
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        decision = yaml.safe_load(yaml_str)
        
        return decision
    
    def post(self, shared, prep_res, exec_res):
        """Save decision and route to next node."""
        logger = get_logger()
        logger.workflow_step("DecideAction.post", "Processing decision")
        
        shared['last_decision'] = exec_res
        
        # Log decision
        logger.decision(exec_res['action'], exec_res)
        
        if exec_res['action'] == 'tool':
            return 'tool'
        else:
            shared['final_answer'] = exec_res['final_answer']
            return 'answer'

class CallTool(Node):
    def prep(self, shared):
        """Prepare tool call from decision."""
        logger = get_logger()
        logger.workflow_step("CallTool.prep", "Preparing tool execution")
        
        decision = shared['last_decision']
        tool_name = decision['tool_name']
        tool_args = decision.get('tool_args', {})
        
        # Get tool function
        tool_info = shared['tool_registry'].get(tool_name)
        if not tool_info:
            logger.error(f"Tool '{tool_name}' not found in registry")
            return None, tool_name, tool_args
            
        return tool_info['function'], tool_name, tool_args
        
    def exec(self, inputs):
        """Execute the tool with provided arguments."""
        logger = get_logger()
        tool_func, tool_name, tool_args = inputs
        
        logger.workflow_step("CallTool.exec", f"Executing tool: {tool_name}")
        
        if tool_func is None:
            error_msg = f"Error: Tool '{tool_name}' not found"
            logger.error(error_msg)
            return error_msg
        
        try:
            # Call tool with arguments
            if isinstance(tool_args, dict):
                result = tool_func(**tool_args)
            else:
                result = tool_func(tool_args)
            
            result_str = str(result)
            
            # Log tool call
            logger.tool_call(tool_name, tool_args, result_str)
            
            return result_str
        except Exception as e:
            error_msg = f"Error calling {tool_name}: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def post(self, shared, prep_res, exec_res):
        """Save tool result and return to decision node."""
        logger = get_logger()
        logger.workflow_step("CallTool.post", "Recording tool result")
        
        tool_func, tool_name, tool_args = prep_res
        
        # Record tool call
        shared['tool_calls'].append({
            'tool': tool_name,
            'args': tool_args,
            'result': exec_res
        })
        
        logger.verbose_log(f"Tool call recorded, returning to decision node")
        
        # Always go back to decide what to do next
        return 'decide'

class ProvideAnswer(Node):
    def prep(self, shared):
        """Get final answer from shared context."""
        logger = get_logger()
        logger.workflow_step("ProvideAnswer.prep", "Preparing final answer")
        return shared.get('final_answer', 'No answer generated')
        
    def exec(self, answer):
        """Return the final answer."""
        logger = get_logger()
        logger.workflow_step("ProvideAnswer.exec", "Finalizing answer")
        return answer
    
    def post(self, shared, prep_res, exec_res):
        """Mark completion."""
        logger = get_logger()
        logger.workflow_step("ProvideAnswer.post", "Workflow complete")
        return 'done' 
