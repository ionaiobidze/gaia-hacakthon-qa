from typing import Optional, List
import os

from cli.args import parse_args
from core.logging import setup_logging, get_logger
from core.engine import AIClient
from core.prompts import PromptConfig, AnalysisMode

logger = get_logger("static_analysis_assistant")


def create_ai_client(args) -> Optional[AIClient]:
    """Create an AI client with appropriate configuration"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("No OPENAI_API_KEY found. AI features will be limited.")
        return None
    
    # Create prompt configuration based on CLI args
    config = PromptConfig()
    
    # Determine analysis mode
    if args.deep_analyze and args.ui:
        config.mode = AnalysisMode.UI_FOCUSED
    elif args.deep_analyze and args.back:
        config.mode = AnalysisMode.BACKEND_FOCUSED
    elif args.deep_analyze:
        config.mode = AnalysisMode.DEEP
    elif args.ui:
        config.mode = AnalysisMode.UI_FOCUSED
    elif args.back:
        config.mode = AnalysisMode.BACKEND_FOCUSED
    else:
        config.mode = AnalysisMode.NORMAL
    
    # Set target language if specified
    if args.language:
        config.target_language = args.language.lower()
        logger.info(f"Target language set to: {config.target_language}")
    
    # Set verbosity level based on CLI args
    config.verbosity_level = 2 if args.verbose else 1
    
    try:
        client = AIClient(
            model="gpt-4",
            api_key=api_key,
            prompt_config=config
        )
        
        # Log the configuration
        config_summary = client.get_prompt_config_summary()
        logger.info(f"AI Client configured: {config_summary['description']}")
        if args.verbose:
            logger.debug(f"Full configuration: {config_summary}")
        
        return client
    except Exception as e:
        logger.error(f"Failed to create AI client: {e}")
        return None


def perform_analysis(deep: bool, targets: List[str], ai_client: Optional[AIClient] = None) -> None:
    """Perform code analysis with optional AI assistance"""
    mode = "deep" if deep else "normal"
    logger.info(f"Running {mode} analysis on: {', '.join(targets)}")
    
    if ai_client:
        logger.info("AI-powered analysis enabled")
        
        # Example files that might be analyzed (this would be expanded)
        example_files = [
            "core/engine.py",
            "core/tools/registry.py",
            "cli/cli.py",
            "main.py"
        ]
        
        try:
            # Use AI to analyze files
            result = ai_client.analyze_files(example_files)
            logger.info("AI analysis completed successfully")
            if result.get("response"):
                print("\n" + "="*50)
                print("AI ANALYSIS RESULTS")
                print("="*50)
                print(result["response"])
                print("="*50 + "\n")
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            logger.info("Falling back to basic analysis")
    else:
        logger.info("Running basic analysis (no AI client available)")
    
    logger.debug("Analysis logic not fully implemented yet.")


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    setup_logging(args.verbose)

    targets: List[str] = []
    if args.ui:
        targets.append("ui")
    if args.back:
        targets.append("back")

    if not targets:
        logger.warning("No targets provided, defaulting to both ui and back")
        targets = ["ui", "back"]

    # Create AI client if possible
    ai_client = create_ai_client(args)
    
    perform_analysis(args.deep_analyze, targets, ai_client)