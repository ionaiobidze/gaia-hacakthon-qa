from typing import Dict, List
from .registry import tool
from .model import Tool

@tool(
    name="read_files",
    desc="Read files on specified paths to check if worthy for tests",
    params={
        "type": "object",
        "properties": {"paths": {"type": "array", "items": {"type": "string"}}},
        "required": ["paths"]
    }
)
class ReadFiles(Tool):
    def __init__(self): self.stats = {"read": 0, "errors": 0}
    def execute(self, args: Dict):
        files = []
        for p in args["paths"]:
            result = self._read_file(p)
            files.append(result)
            if "error" in result: self.stats["errors"] += 1
            else: self.stats["read"] += 1
        return files
    def _read_file(self, path: str):
        try:
            with open(path, 'r') as f:
                content = f.read()
                return {"path": path, "content": content, "worthy": self._is_worthy(path, content)}
        except: return {"path": path, "error": "read_fail", "worthy": False}
    def _is_worthy(self, path: str, content: str): return len(content) > 0 and not content.isspace()
    def schema(self):
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
    name="summary",
    desc="Return summarization of generated tests",
    params={
        "type": "object",
        "properties": {"content": {"type": "string"}},
        "required": ["content"]
    }
)
class Summary(Tool):
    def __init__(self): self.keywords = ['test', 'assert', 'expect', 'mock']
    def execute(self, args: Dict):
        content = args["content"]
        stats = self._analyze_content(content)
        return self._format_summary(stats)
    def _analyze_content(self, content: str):
        lines = content.split('\n')
        return {
            "total_lines": len(lines),
            "test_methods": len([l for l in lines if 'test' in l.lower()]),
            "assertions": len([l for l in lines if any(k in l.lower() for k in self.keywords)]),
            "non_empty": len([l for l in lines if l.strip()])
        }
    def _format_summary(self, stats: Dict): return f"Generated {stats['test_methods']} test methods, {stats['assertions']} assertions across {stats['total_lines']} lines"
    def schema(self):
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
