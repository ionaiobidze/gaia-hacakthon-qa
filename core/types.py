from dataclasses import dataclass
from typing import Optional


@dataclass
class CLIArgs:
    deep_analyze: bool
    ui: bool
    back: bool
    verbose: bool
    language: Optional[str] = None 