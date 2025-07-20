from typing import Dict, Any, List
from abc import ABC, abstractmethod

class Tool(ABC):
    @abstractmethod
    def execute(self, args: Dict) -> Any: pass
    @abstractmethod
    def schema(self) -> Dict: pass

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

@tool(
    name="read_files",
    desc="Read files on specified paths to check if worthy for tests",
    params={
        "type": "object",
        "properties": {"paths": {"type": "array", "items": {"type": "string"}}},
        "required": ["paths"]})
class ReadFiles(Tool):
    def __init__(self):
        self.stats = {"read": 0, "errors": 0}

    def execute(self, args: Dict) -> List[Dict]:
        files = []
        for p in args["paths"]:
            result = self._read_file(p)
            files.append(result)
            if "error" in result: self.stats["errors"] += 1
            else: self.stats["read"] += 1
        return files

    def _read_file(self, path: str) -> Dict:
        try:
            with open(path, 'r') as f:
                content = f.read()
                return {"path": path, "content": content, "worthy": self._is_worthy(path, content)}
        except: return {"path": path, "error": "read_fail", "worthy": False}
    def _is_worthy(self, path: str, content: str): return len(content) > 0 and not content.isspace()
    def schema(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": "read_files",
                "description": "Read files on specified paths to check if worthy for tests",
                "parameters": {
                    "type": "object",
                    "properties": {"paths": {"type": "array", "items": {"type": "string"}}},
                    "required": ["paths"]
                }
            }
        }

@tool(
    "pick_files",
    "Return paths necessary to generate tests for",
    {
        "type": "object",
        "properties": {"paths": {"type": "array", "items": {"type": "string"}}},
        "required": ["paths"]
    }
)
class PickFiles(Tool):
    def __init__(self):
        self.extensions = ('.java', '.py', '.js', '.ts', '.kt')
        self.stats = {"picked": 0, "skipped": 0}
    def execute(self, args: Dict) -> List[str]:
        worthy = []
        for p in args["paths"]:
            if self._is_testable(p):
                worthy.append(p)
                self.stats["picked"] += 1
            else: self.stats["skipped"] += 1
        return worthy
    def _is_testable(self, path: str): return path.endswith(self.extensions) and not self._is_test_file(path)
    def _is_test_file(self, path: str): return 'test' in path.lower() or 'spec' in path.lower()
    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": "pick_files",
                "description": "Return paths necessary to generate tests for",
                "parameters": {
                    "type": "object",
                    "properties": {"paths": {"type": "array", "items": {"type": "string"}}},
                    "required": ["paths"]
                }
            }
        }

@tool(
    "summary",
    "Return summarization of generated tests",
    {
        "type": "object",
        "properties": {"content": {"type": "string"}},
        "required": ["content"]
    }
)
class Summary(Tool):
    def __init__(self):
        self.keywords = ['test', 'assert', 'expect', 'mock']

    def execute(self, args: Dict) -> str:
        content = args["content"]
        stats = self._analyze_content(content)
        return self._format_summary(stats)

    def _analyze_content(self, content: str) -> Dict:
        lines = content.split('\n')
        return {
            "total_lines": len(lines),
            "test_methods": len([l for l in lines if 'test' in l.lower()]),
            "assertions": len([l for l in lines if any(k in l.lower() for k in self.keywords)]),
            "non_empty": len([l for l in lines if l.strip()])
        }

    def _format_summary(self, stats: Dict) -> str:
        return f"Generated {stats['test_methods']} test methods, {stats['assertions']} assertions across {stats['total_lines']} lines"

    def schema(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": "summary",
                "description": "Return summarization of generated tests",
                "parameters": {
                    "type": "object",
                    "properties": {"content": {"type": "string"}},
                    "required": ["content"]
                }
            }
        }

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

    def schemas(self) -> List[Dict]:
        return [tool.schema() for tool in self._tools.values()]

