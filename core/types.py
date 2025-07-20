from dataclasses import dataclass
from typing import Optional


@dataclass
class CLIArgs:
    deep_analyze: bool
    ui: bool
    back: bool
    verbose: bool
    swagger_path: Optional[str] = None
    message: Optional[str] = None 
