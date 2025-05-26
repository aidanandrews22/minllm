from minllm import Flow
from .nodes import DecideAction, CallTool, ProvideAnswer
from .logger import get_logger

def create_agent_flow(tool_registry):
    """Create agent flow that can use any provided tools.
    
    Args:
        tool_registry: Dictionary of available tools
        
    Returns:
        Flow: Complete agent flow with dynamic tool calling
    """
    logger = get_logger()
    num_tools = len(tool_registry)
    logger.verbose_log(f"Creating agent flow with {num_tools} tools")
    
    # Create node instances
    decide = DecideAction()
    call_tool = CallTool()
    provide_answer = ProvideAnswer()
    
    # Connect nodes
    decide - "tool" >> call_tool
    decide - "answer" >> provide_answer
    call_tool - "decide" >> decide
    
    logger.verbose_log("Flow connections established")
    
    # Start with decision node
    return Flow(start=decide) 