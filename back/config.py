"""
Configuration management for backend AI agent
"""
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if available
except ImportError:
    pass  # dotenv is optional


@dataclass
class BackendConfig:
    """Configuration for backend analysis"""
    openai_api_key: str
    swagger_path: Optional[str] = None
    output_dir: str = "tests"
    model: str = "gpt-4.1-mini"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    @classmethod
    def from_env(cls) -> "BackendConfig":
        """Create config from environment variables"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        return cls(
            openai_api_key=api_key,
            swagger_path=os.getenv("SWAGGER_PATH"),
            output_dir=os.getenv("OUTPUT_DIR", "tests"),
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            max_tokens=int(os.getenv("MAX_TOKENS", "4000")),
            temperature=float(os.getenv("TEMPERATURE", "0.1"))
        ) 