"""
Configuration examples and utilities for prompt management
"""

from typing import Dict, Any
import json
from .templates import PromptConfig, AnalysisMode


class ConfigPresets:
    """Predefined configuration presets for common use cases"""
    
    # Basic analysis configurations
    QUICK_SCAN = PromptConfig(
        mode=AnalysisMode.NORMAL,
        verbosity_level=1,
        include_examples=False
    )
    
    COMPREHENSIVE_ANALYSIS = PromptConfig(
        mode=AnalysisMode.DEEP,
        verbosity_level=3,
        include_examples=True
    )
    
    # Language-specific presets
    PYTHON_FOCUS = PromptConfig(
        mode=AnalysisMode.NORMAL,
        target_language="python",
        verbosity_level=2
    )
    
    TYPESCRIPT_REACT = PromptConfig(
        mode=AnalysisMode.UI_FOCUSED,
        target_language="typescript",
        verbosity_level=2
    )
    
    JAVA_BACKEND = PromptConfig(
        mode=AnalysisMode.BACKEND_FOCUSED,
        target_language="java",
        verbosity_level=2
    )
    
    # Team-specific configurations
    FRONTEND_TEAM = PromptConfig(
        mode=AnalysisMode.UI_FOCUSED,
        target_language="typescript",
        verbosity_level=2,
        include_examples=True
    )
    
    BACKEND_TEAM = PromptConfig(
        mode=AnalysisMode.BACKEND_FOCUSED,
        target_language="python",
        verbosity_level=2,
        include_examples=True
    )
    
    QA_TEAM = PromptConfig(
        mode=AnalysisMode.DEEP,
        verbosity_level=3,
        include_examples=True
    )

    @classmethod
    def get_preset(cls, name: str) -> PromptConfig:
        """Get a preset configuration by name"""
        presets = {
            "quick": cls.QUICK_SCAN,
            "comprehensive": cls.COMPREHENSIVE_ANALYSIS,
            "python": cls.PYTHON_FOCUS,
            "typescript": cls.TYPESCRIPT_REACT,
            "react": cls.TYPESCRIPT_REACT,
            "java": cls.JAVA_BACKEND,
            "frontend": cls.FRONTEND_TEAM,
            "backend": cls.BACKEND_TEAM,
            "qa": cls.QA_TEAM
        }
        
        if name.lower() not in presets:
            available = ", ".join(presets.keys())
            raise ValueError(f"Unknown preset '{name}'. Available presets: {available}")
        
        return presets[name.lower()]
    
    @classmethod
    def list_presets(cls) -> Dict[str, str]:
        """List all available presets with descriptions"""
        return {
            "quick": "Fast analysis with minimal verbosity",
            "comprehensive": "Deep analysis with maximum detail",
            "python": "Python-focused analysis",
            "typescript": "TypeScript/React UI analysis",
            "react": "TypeScript/React UI analysis (alias)",
            "java": "Java backend analysis",
            "frontend": "Frontend team configuration",
            "backend": "Backend team configuration",
            "qa": "QA team comprehensive testing focus"
        }


def load_config_from_file(file_path: str) -> PromptConfig:
    """Load configuration from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Convert mode string to enum
        if 'mode' in data:
            data['mode'] = AnalysisMode(data['mode'])
        
        return PromptConfig(**data)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")
    except Exception as e:
        raise ValueError(f"Error loading configuration: {e}")


def save_config_to_file(config: PromptConfig, file_path: str) -> None:
    """Save configuration to a JSON file"""
    data = {
        "mode": config.mode.value,
        "target_language": config.target_language,
        "include_examples": config.include_examples,
        "verbosity_level": config.verbosity_level
    }
    
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise ValueError(f"Error saving configuration: {e}")


# Example configuration file content
EXAMPLE_CONFIG = {
    "mode": "deep",
    "target_language": "python",
    "include_examples": True,
    "verbosity_level": 2
}

# Documentation for configuration options
CONFIG_DOCUMENTATION = """
Static Analysis Assistant - Configuration Options

## Analysis Modes:
- normal: Standard analysis with balanced speed and depth
- deep: Comprehensive analysis including complexity metrics
- ui_focused: Frontend-focused analysis for UI components
- backend_focused: Backend-focused analysis for APIs and business logic

## Supported Languages:
- python: Python-specific testing guidance
- javascript: JavaScript/Node.js guidance
- typescript: TypeScript-specific guidance
- java: Java testing best practices
- kotlin: Kotlin/Android testing guidance

## Verbosity Levels:
- 1: Minimal output, focus on results
- 2: Standard output with explanations
- 3: Detailed output with comprehensive reasoning

## Example Configuration File (config.json):
{
    "mode": "deep",
    "target_language": "python",
    "include_examples": true,
    "verbosity_level": 2
}

## Usage:
python main.py --lang python --deep --verbose
""" 