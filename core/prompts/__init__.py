# Prompt management module
from .manager import PromptManager
from .templates import SystemPrompts, PromptTemplates, AnalysisMode, PromptConfig
from .config import ConfigPresets, load_config_from_file, save_config_to_file, CONFIG_DOCUMENTATION

# Import legacy constants from the standalone prompts.py file for backward compatibility
import sys
from pathlib import Path
import importlib.util

# Load the standalone prompts.py file
_prompts_file = Path(__file__).parent.parent / 'prompts.py'
if _prompts_file.exists():
    spec = importlib.util.spec_from_file_location("legacy_prompts", _prompts_file)
    legacy_prompts = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy_prompts)
    
    # Export legacy constants
    SYSTEM_PROMPT = legacy_prompts.SYSTEM_PROMPT
    FUNCTION_SCHEMA = legacy_prompts.FUNCTION_SCHEMA

__all__ = [
    'PromptManager', 
    'SystemPrompts', 
    'PromptTemplates', 
    'AnalysisMode', 
    'PromptConfig',
    'ConfigPresets',
    'load_config_from_file',
    'save_config_to_file',
    'CONFIG_DOCUMENTATION',
    'SYSTEM_PROMPT',
    'FUNCTION_SCHEMA'
] 