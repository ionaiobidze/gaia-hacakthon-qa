import argparse
from typing import Optional, List

from core.types import CLIArgs


def parse_args(argv: Optional[List[str]] = None) -> CLIArgs:
    parser = argparse.ArgumentParser(
        description="Static Analysis Assistant - AI-powered code analysis and test generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ui --deep                 # Deep analysis of UI components
  %(prog)s --back --verbose            # Backend analysis with verbose output
  %(prog)s --ui --back --lang python   # Analyze both UI and backend for Python
  %(prog)s --deep --lang typescript    # Deep analysis with TypeScript-specific guidance
        """
    )

    parser.add_argument("--deep-analyze", "--deep", action="store_true", help="Enable deep analysis mode")
    parser.add_argument("--ui", action="store_true", help="Analyze UI layer")
    parser.add_argument("--back", action="store_true", help="Analyze backend layer")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--swagger-path", "--swagger", type=str, help="Path to swagger/OpenAPI JSON file")
    parser.add_argument("--message", "-m", type=str, help="Custom message/requirements for test generation")

    args = parser.parse_args(argv)

    return CLIArgs(
        deep_analyze=args.deep_analyze,
        ui=args.ui,
        back=args.back,
        verbose=args.verbose,
        swagger_path=args.swagger_path,
        message=args.message,
    ) 