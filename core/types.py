from dataclasses import dataclass


@dataclass
class CLIArgs:
    deep_analyze: bool
    ui: bool
    back: bool
    verbose: bool 