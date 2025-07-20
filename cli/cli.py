from typing import Optional, List
import json

from cli.args import parse_args
from core.logging import setup_logging, get_logger
from core.engine import AIClient
from core.prompts import PromptConfig, AnalysisMode

logger = get_logger("static_analysis_assistant")


def perform_analysis(deep: bool, targets: List[str], swagger_path: Optional[str] = None, user_message: Optional[str] = None) -> None:
    """Perform analysis based on targets"""
    logger.info(f"Running analysis on: {', '.join(targets)}")
    
    # Perform deep analysis first if enabled
    if deep:
        perform_deep_analysis(targets)
    
    if "back" in targets:
        write_tests(swagger_path, user_message)
    
    if "ui" in targets:
        perform_ui_analysis()


def write_tests(swagger_path: Optional[str] = None, user_message: Optional[str] = None) -> dict:
    """Write pytest tests from swagger specification"""
    try:
        from back import TestWriter
        
        if not swagger_path:
            raise ValueError("No swagger file path provided. Use --swagger argument.")
        
        logger.info("Starting test generation")
        
        # Load swagger JSON
        with open(swagger_path, 'r', encoding='utf-8') as f:
            swagger_data = json.load(f)
        
        logger.info(f"Loaded swagger file: {swagger_path}")
        
        writer = TestWriter()
        
        # Generate tests with user message
        result = writer.write_tests(swagger_data, user_message)
        
        if result["status"] == "success":
            logger.info("Test generation completed successfully")
            logger.info(f"Generated {len(result['generated_files'])} files")
        else:
            logger.error(f"Test generation failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except ImportError as e:
        error_msg = f"Test generation dependencies not available: {e}"
        logger.error(error_msg)
        return {"status": "error", "error": error_msg}
    except Exception as e:
        error_msg = f"Test generation failed: {e}"
        logger.error(error_msg)
        return {"status": "error", "error": error_msg}


def perform_deep_analysis(targets: List[str]) -> None:
    """Perform deep analysis using the AI engine with automatic file discovery"""
    try:
        from core.engine import AIClient
        import os
        
        logger.info("Starting deep analysis with automatic file discovery")
        
        # Initialize AI client
        client = AIClient()
        
        # Update client configuration based on targets
        ui_focused = "ui" in targets
        backend_focused = "back" in targets
        client.update_from_cli_args(deep_analyze=True, ui=ui_focused, back=backend_focused)
        
        # Get project files using the automatic file picker
        files = client._get_project_file_paths()
        logger.info(f"Discovered {len(files)} project files")
        logger.info(f"Files to analyze: {', '.join(files[:10])}{'...' if len(files) > 10 else ''}")
        
        # If OPENAI_API_KEY is available, perform AI analysis
        if os.getenv("OPENAI_API_KEY"):
            from back.config import BackendConfig
            config = BackendConfig.from_env()
            client = AIClient(api_key=config.openai_api_key)
            client.update_from_cli_args(deep_analyze=True, ui=ui_focused, back=backend_focused)
            
            result = client.analyze_files(files)
            logger.info("Deep analysis completed")
            logger.info(f"Analysis response: {result.get('response', 'No response')}")
        else:
            logger.info("OPENAI_API_KEY not set - skipping AI analysis, showing discovered files only")
        
    except Exception as e:
        logger.error(f"Deep analysis failed: {e}")


def perform_ui_analysis() -> None:
    """Placeholder for UI analysis"""
    logger.info("UI analysis not implemented yet")


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    setup_logging(args.verbose)

    targets: List[str] = []
    if args.ui:
        targets.append("ui")
    if args.back:
        targets.append("back")

    if not targets:
        print("No targets specified.")
        return

    perform_analysis(args.deep_analyze, targets, args.swagger_path, args.message)