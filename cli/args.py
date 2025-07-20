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

    # Analysis mode arguments
    parser.add_argument("--deep-analyze", "--deep", action="store_true", 
                       help="Enable deep analysis mode with comprehensive code analysis")
    parser.add_argument("--ui", action="store_true", 
                       help="Analyze UI/Frontend layer with focus on components and interactions")
    parser.add_argument("--back", action="store_true", 
                       help="Analyze backend/API layer with focus on business logic")
    
    # Language and prompt configuration
    parser.add_argument("--lang", "--language", type=str, 
                       help="Target programming language (python, javascript, typescript, java, kotlin)")
    
    # Output and logging
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output with detailed logging")

    args = parser.parse_args(argv)

    return CLIArgs(
        deep_analyze=args.deep_analyze,
        ui=args.ui,
        back=args.back,
        verbose=args.verbose,
        language=getattr(args, 'lang', None)
    ) 