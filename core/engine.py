# Main orchestration logic
from typing import Dict, Any, List, Optional, Union, cast
from .generator import ToolRegistry
from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import json

class ConversationContext:
    def __init__(self) -> None:
        self.messages: List[ChatCompletionMessageParam] = []
        self.metadata: Dict[str, Any] = {}

    def add_user_message(self, content: str) -> None:
        self.messages.append(cast(ChatCompletionMessageParam, {"role": "user", "content": content}))

    def add_assistant_message(self, content: str) -> None:
        self.messages.append(cast(ChatCompletionMessageParam, {"role": "assistant", "content": content}))

    def add_system_message(self, content: str) -> None:
        self.messages.append(cast(ChatCompletionMessageParam, {"role": "system", "content": content}))

    def add_tool_message(self, tool_call_id: str, content: str) -> None:
        self.messages.append(cast(ChatCompletionMessageParam, {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content
        }))

    def get_messages(self) -> List[ChatCompletionMessageParam]:
        return self.messages.copy()

    def clear(self) -> None:
        self.messages.clear()
        self.metadata.clear()

    def set_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)

class AIClient:
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.model = model
        self.base_url = base_url
        self.registry = ToolRegistry()
        self.context = ConversationContext()
        self.client: Optional[OpenAI] = None
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)

    def call(self, prompt: str) -> Dict[str, Any]:
        if not self.client:
            raise ValueError("OpenAI client not initialized. Provide api_key to constructor.")

        self.context.add_user_message(prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.context.get_messages(),
            tools=cast(Any, self.registry.schemas()),
            tool_choice="auto"
        )
        return self._handle_response(response)

    def _handle_response(self, response: ChatCompletion) -> Dict[str, Any]:
        message = response.choices[0].message
        self.context.add_assistant_message(message.content or "")

        if message.tool_calls:
            for tool_call in message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                result = self.registry.execute(name, args)

                self.context.add_tool_message(tool_call.id, json.dumps(result))

            # Get final response after tool execution with summary instruction
            self.context.add_system_message("Always end your response with a summary of actions taken and results.")
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

        return {"messages": self.context.get_messages(), "response": message.content or ""}

    def exec_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        return self.registry.execute(tool_name, args)

    def clear_conversation(self) -> None:
        """Clear the conversation history"""
        self.context.clear()

    def get_conversation_history(self) -> List[ChatCompletionMessageParam]:
        """Get the full conversation history"""
        return self.context.get_messages()

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata for the conversation"""
        self.context.set_metadata(key, value)

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the conversation"""
        return self.context.get_metadata(key, default)

