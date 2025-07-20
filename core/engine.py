# Main orchestration logic
from typing import Dict, Any, List, Optional, cast
from .tools.registry import ToolRegistry
from .prompts import PromptManager, AnalysisMode, PromptConfig
from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import json
import os
from pathlib import Path
from pathspec import PathSpec

class ConversationContext:
    def __init__(self):
        self.messages: List[ChatCompletionMessageParam] = []
        self.metadata: Dict[str, Any] = {}

    def add_user_message(self, content: str):
        self.messages.append(cast(ChatCompletionMessageParam, {"role": "user", "content": content}))

    def add_assistant_message(self, content: str, tool_calls=None):
        message = {"role": "assistant", "content": content}
        if tool_calls:
            message["tool_calls"] = tool_calls
        self.messages.append(cast(ChatCompletionMessageParam, message))

    def add_system_message(self, content: str):
        self.messages.append(cast(ChatCompletionMessageParam, {"role": "system", "content": content}))

    def add_tool_message(self, tool_call_id: str, content: str):
        self.messages.append(cast(ChatCompletionMessageParam, {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content
        }))

    def get_messages(self) -> List[ChatCompletionMessageParam]:
        return self.messages.copy()

    def clear(self):
        self.messages.clear()
        self.metadata.clear()

    def set_metadata(self, key: str, value: Any):
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None):
        return self.metadata.get(key, default)

class AIClient:
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None, prompt_config: Optional[PromptConfig] = None):
        self.model = model
        self.registry = ToolRegistry()
        self.context = ConversationContext()
        self.prompt_manager = PromptManager(prompt_config)
        self.client: Optional[OpenAI] = None
        self._system_prompt_set = False
        
        if api_key:
            self.client = OpenAI(api_key=api_key)

    def _ensure_system_prompt(self):
        """Ensure the system prompt is set at the beginning of conversation"""
        if not self._system_prompt_set:
            system_prompt = self.prompt_manager.get_system_prompt()
            self.context.add_system_message(system_prompt)
            self._system_prompt_set = True

    def call(self, prompt: str):
        if not self.client:
            raise ValueError("OpenAI client not initialized. Provide api_key to constructor.")

        self._ensure_system_prompt()
        self.context.add_user_message(prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.context.get_messages(),
            tools=cast(Any, self.registry.schemas()),
            tool_choice="auto"
        )
        return self._handle_response(response)

    def _handle_response(self, response: ChatCompletion):
        message = response.choices[0].message

        if message.tool_calls:
            # Add the assistant message with tool calls
            self.context.add_assistant_message(message.content or "", tool_calls=message.tool_calls)
            
            # Execute tools and add tool messages
            for tool_call in message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                result = self.registry.execute(name, args)
                self.context.add_tool_message(tool_call.id, json.dumps(result))

            # Get final response after tool execution with improved summary instruction
            summary_prompt = self.prompt_manager.get_tool_execution_summary_prompt()
            self.context.add_system_message(summary_prompt)
            
            if self.client:
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.context.get_messages(),
                    tools=cast(Any, self.registry.schemas())
                )
                final_content = final_response.choices[0].message.content or ""
                self.context.add_assistant_message(final_content)
                return {"messages": self.context.get_messages(), "response": final_content}
            else:
                return {"messages": self.context.get_messages(), "response": ""}
        else:
            # No tool calls, just add the assistant message
            self.context.add_assistant_message(message.content or "")

        return {"messages": self.context.get_messages(), "response": message.content or ""}

    def exec_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        return self.registry.execute(tool_name, args)

    def clear_conversation(self) -> None:
        """Clear the conversation history"""
        self.context.clear()
        self._system_prompt_set = False

    def get_conversation_history(self) -> List[ChatCompletionMessageParam]:
        """Get the full conversation history"""
        return self.context.get_messages()

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata for the conversation"""
        self.context.set_metadata(key, value)

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the conversation"""
        return self.context.get_metadata(key, default)

    # New prompt management methods
    def set_analysis_mode(self, mode: AnalysisMode) -> None:
        """Set the analysis mode for the AI assistant"""
        self.prompt_manager.set_mode(mode)
        # Reset system prompt to apply new mode
        if self._system_prompt_set:
            self.clear_conversation()

    def set_target_language(self, language: str) -> None:
        """Set the target programming language for analysis"""
        self.prompt_manager.set_target_language(language)
        # Reset system prompt to apply new language settings
        if self._system_prompt_set:
            self.clear_conversation()

    def update_from_cli_args(self, deep_analyze: bool = False, ui: bool = False, back: bool = False) -> None:
        """Update prompt configuration based on CLI arguments"""
        self.prompt_manager.update_from_cli_args(deep_analyze, ui, back)
        # Reset system prompt to apply new settings
        if self._system_prompt_set:
            self.clear_conversation()

    def get_prompt_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current prompt configuration"""
        return self.prompt_manager.get_config_summary()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_project_file_paths(self, root_path: str = ".") -> List[str]:
        """Return a list of project files respecting .gitignore rules."""
        gitignore_path = Path(root_path) / ".gitignore"
        patterns = []
        
        if gitignore_path.exists():
            patterns = gitignore_path.read_text().splitlines()
        
        # Always exclude .git directory
        patterns.append(".git/")
        patterns.append(".git/**")
        
        spec = PathSpec.from_lines("gitwildmatch", patterns)
        
        file_paths: List[str] = []
        for path in Path(root_path).rglob("*"):
            if path.is_file():
                rel_path = path.relative_to(root_path).as_posix()
                if not spec.match_file(rel_path):
                    file_paths.append(rel_path)
        
        return file_paths

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_files(self, file_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze repository files with context-aware prompts.

        If *file_paths* is ``None`` the method automatically discovers all
        relevant source files under *root_path* while respecting ``.gitignore``.
        This makes it convenient to perform *deep* analysis without the caller
        having to build the list manually.
        """

        if file_paths is None:
            file_paths = self._get_project_file_paths()

        if not self.client:
            raise ValueError("OpenAI client not initialized. Provide api_key to constructor.")

        # Generate a context-aware prompt for file analysis.
        analysis_prompt = self.prompt_manager.get_file_analysis_prompt(file_paths)
        return self.call(analysis_prompt)