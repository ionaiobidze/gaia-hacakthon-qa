from typing import Dict, Any, List
from .model import Tool

_registered_tools = []

def tool(name: str, desc: str, params: Dict):
    def decorator(target):
        class_instance = None
        if not isinstance(target, type):
            class FuncTool(Tool):
                def execute(self, args: Dict) -> Any: return target(args)
                def schema(self) -> Dict:
                    return {
                        "type": "function",
                        "function": {"name": name, "description": desc, "parameters": params}
                    }
            class_instance = FuncTool()
        else: class_instance = target()
        _registered_tools.append((name, class_instance))
        return target
    return decorator

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._register_decorated()
    def _register_decorated(self):
        for name, tool_instance in _registered_tools:
            self.register(name, tool_instance)
    def register(self, name: str, tool: Tool): self._tools[name] = tool
    def execute(self, name: str, args: Dict) -> Any:
        if name not in self._tools: raise ValueError(f"Unknown tool: {name}")
        return self._tools[name].execute(args)
    def schemas(self) -> List[Dict]: return [tool.schema() for tool in self._tools.values()]

