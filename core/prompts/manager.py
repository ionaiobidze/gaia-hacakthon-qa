"""
Prompt Manager for handling system prompts and configuration
"""

from typing import Dict, Any, Optional, List
from .templates import SystemPrompts, PromptTemplates, AnalysisMode, PromptConfig


class PromptManager:
    """Manages system prompts and prompt configuration for the AI assistant"""
    
    def __init__(self, config: Optional[PromptConfig] = None):
        self.config = config or PromptConfig()
        self._system_prompt = None
        self._cached_prompts: Dict[str, str] = {}
    
    def set_config(self, config: PromptConfig) -> None:
        """Update the prompt configuration"""
        self.config = config
        self._system_prompt = None  # Clear cache
        self._cached_prompts.clear()
    
    def set_mode(self, mode: AnalysisMode) -> None:
        """Set the analysis mode"""
        self.config.mode = mode
        self._system_prompt = None  # Clear cache
    
    def set_target_language(self, language: str) -> None:
        """Set the target programming language"""
        self.config.target_language = language
        self._system_prompt = None  # Clear cache
    
    def get_system_prompt(self) -> str:
        """Get the current system prompt based on configuration"""
        if self._system_prompt is None:
            self._system_prompt = SystemPrompts.get_system_prompt(self.config)
        return self._system_prompt
    
    def get_file_analysis_prompt(self, file_paths: List[str]) -> str:
        """Get a formatted file analysis prompt"""
        cache_key = f"file_analysis_{hash(tuple(file_paths))}"
        if cache_key not in self._cached_prompts:
            self._cached_prompts[cache_key] = PromptTemplates.format_file_analysis_prompt(file_paths)
        return self._cached_prompts[cache_key]
    
    def get_summary_prompt(self, test_content: str) -> str:
        """Get a formatted summary prompt"""
        return PromptTemplates.format_summary_prompt(test_content)
    
    def get_tool_execution_summary_prompt(self) -> str:
        """Get the tool execution summary prompt"""
        return PromptTemplates.TOOL_EXECUTION_SUMMARY
    
    def get_mode_description(self) -> str:
        """Get a description of the current analysis mode"""
        descriptions = {
            AnalysisMode.NORMAL: "Standard code analysis with balanced depth and speed",
            AnalysisMode.DEEP: "Comprehensive analysis including complexity metrics and architectural considerations",
            AnalysisMode.UI_FOCUSED: "Frontend-focused analysis prioritizing UI components and user interactions",
            AnalysisMode.BACKEND_FOCUSED: "Backend-focused analysis prioritizing business logic and API endpoints"
        }
        return descriptions.get(self.config.mode, "Unknown analysis mode")
    
    def update_from_cli_args(self, deep_analyze: bool = False, ui: bool = False, back: bool = False) -> None:
        """Update configuration based on CLI arguments"""
        # Determine mode based on CLI flags
        if deep_analyze and ui:
            mode = AnalysisMode.UI_FOCUSED
        elif deep_analyze and back:
            mode = AnalysisMode.BACKEND_FOCUSED
        elif deep_analyze:
            mode = AnalysisMode.DEEP
        elif ui:
            mode = AnalysisMode.UI_FOCUSED
        elif back:
            mode = AnalysisMode.BACKEND_FOCUSED
        else:
            mode = AnalysisMode.NORMAL
        
        # Update configuration
        self.config.mode = mode
        self._system_prompt = None  # Clear cache
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            "mode": self.config.mode.value,
            "target_language": self.config.target_language,
            "include_examples": self.config.include_examples,
            "verbosity_level": self.config.verbosity_level,
            "description": self.get_mode_description()
        }
    
    @classmethod
    def create_for_mode(cls, mode: AnalysisMode, **kwargs) -> 'PromptManager':
        """Factory method to create a PromptManager for a specific mode"""
        config = PromptConfig(mode=mode, **kwargs)
        return cls(config)
    
    @classmethod
    def create_for_language(cls, language: str, **kwargs) -> 'PromptManager':
        """Factory method to create a PromptManager for a specific language"""
        config = PromptConfig(target_language=language, **kwargs)
        return cls(config) 