import argparse
from typing import Optional, List

from core.types import CLIArgs


def parse_args(argv: Optional[List[str]] = None) -> CLIArgs:
    parser = argparse.ArgumentParser(
        description="Static Analysis Assistant",
    )

    parser.add_argument("--deep-analyze", "--deep", action="store_true", help="Enable deep analysis mode")
    parser.add_argument("--ui", action="store_true", help="Analyze UI layer")
    parser.add_argument("--back", action="store_true", help="Analyze backend layer")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args(argv)

    return CLIArgs(
        deep_analyze=args.deep_analyze,
        ui=args.ui,
        back=args.back,
        verbose=args.verbose,
    ) 