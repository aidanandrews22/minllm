"""Logging utilities for MinAgent framework."""

import json
from typing import Any

class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'

class Logger:
    """Beautiful logger for agent operations."""
    
    def __init__(self, enabled=False, verbose=False):
        self.enabled = enabled
        self.verbose = verbose
    
    def _format_content(self, content: str, max_length: int = 100) -> str:
        """Format content - always return full content."""
        return content
    
    def _print_section(self, title: str, color: str, content: str = None):
        """Print a formatted section."""
        if not self.enabled:
            return
            
        print(f"\n{color}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
        print(f"{color}{Colors.BOLD}  {title}{Colors.RESET}")
        print(f"{color}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
        
        if content:
            print(f"{Colors.WHITE}{content}{Colors.RESET}")
    
    def _print_item(self, label: str, value: Any, color: str = Colors.CYAN):
        """Print a labeled item."""
        if not self.enabled:
            return
            
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, indent=2)
        else:
            value_str = str(value)
            
        formatted_value = self._format_content(value_str)
        print(f"{color}{Colors.BOLD}{label}:{Colors.RESET} {formatted_value}")
    
    def agent_start(self, query: str):
        """Log agent execution start."""
        if not self.enabled:
            return
            
        self._print_section("🤖 AGENT EXECUTION", Colors.BLUE)
        self._print_item("Query", query, Colors.WHITE)
    
    def llm_call(self, prompt: str, response: str):
        """Log LLM input/output."""
        if not self.enabled:
            return
            
        self._print_section("🧠 LLM CALL", Colors.MAGENTA)
        self._print_item("Input", prompt, Colors.GRAY)
        self._print_item("Output", response, Colors.WHITE)
    
    def tool_call(self, tool_name: str, args: dict, result: str):
        """Log tool execution."""
        if not self.enabled:
            return
            
        self._print_section(f"🔧 TOOL: {tool_name}", Colors.GREEN)
        if args:
            self._print_item("Arguments", args, Colors.YELLOW)
        self._print_item("Result", result, Colors.WHITE)
    
    def decision(self, action: str, details: dict):
        """Log agent decision."""
        if not self.enabled:
            return
            
        icon = "🔧" if action == "tool" else "✅"
        self._print_section(f"{icon} DECISION: {action.upper()}", Colors.CYAN)
        
        if action == "tool":
            self._print_item("Tool", details.get('tool_name', 'Unknown'))
            if details.get('tool_args'):
                self._print_item("Args", details['tool_args'])
        else:
            self._print_item("Answer", details.get('final_answer', 'No answer'))
    
    def final_answer(self, answer: str):
        """Log final answer."""
        if not self.enabled:
            return
            
        self._print_section("✨ FINAL ANSWER", Colors.GREEN)
        print(f"{Colors.WHITE}{answer}{Colors.RESET}")
    
    def verbose_log(self, message: str, color: str = Colors.GRAY):
        """Log verbose workflow messages."""
        if not self.verbose:
            return
            
        print(f"{color}{Colors.DIM}→ {message}{Colors.RESET}")
    
    def error(self, message: str):
        """Log error messages."""
        if not self.enabled:
            return
            
        print(f"{Colors.RED}{Colors.BOLD}❌ ERROR: {message}{Colors.RESET}")
    
    def workflow_step(self, step: str, details: str = None):
        """Log workflow step entry."""
        if not self.verbose:
            return
            
        print(f"\n{Colors.BLUE}{Colors.DIM}📍 {step}{Colors.RESET}")
        if details:
            print(f"{Colors.GRAY}{Colors.DIM}   {details}{Colors.RESET}")

# Global logger instance
_logger = Logger()

def set_logging(enabled: bool, verbose: bool = False):
    """Configure global logging settings."""
    global _logger
    _logger = Logger(enabled, verbose)

def get_logger() -> Logger:
    """Get the global logger instance."""
    return _logger 