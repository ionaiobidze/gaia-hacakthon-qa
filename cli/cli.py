from typing import Optional, List
import json
import dotenv
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.align import Align

from cli.args import parse_args
from core.logging import setup_logging, get_logger
from core.engine import AIClient
from core.prompts import PromptConfig, AnalysisMode

logger = get_logger("static_analysis_assistant")
console = Console()

dotenv.load_dotenv()

def create_backend_step_panel(step_num: int, title: str, description: str, status: str = "running"):
    """Create a beautiful step panel for backend operations"""
    status_icons = {
        "running": "🔄",
        "success": "✅",
        "failure": "❌",
        "pending": "⏳"
    }
    
    status_colors = {
        "running": "yellow",
        "success": "green", 
        "failure": "red",
        "pending": "blue"
    }
    
    icon = status_icons.get(status, "⏳")
    color = status_colors.get(status, "white")
    
    content = f"{icon} [bold]{title}[/bold]\n{description}"
    
    return Panel(
        content,
        title=f"[bold {color}]STEP {step_num}[/bold {color}]",
        border_style=color,
        box=box.ROUNDED,
        padding=(1, 2)
    )

def print_backend_summary_table(results: dict):
    """Display elegant backend results summary"""
    table = Table(
        title="📊 Backend Analysis Summary",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Value", style="green", width=15)
    table.add_column("Details", style="white", width=40)
    
    table.add_row("Status", results.get('status', 'Unknown'), results.get('status_details', ''))
    table.add_row("Generated Files", str(results.get('generated_files_count', 0)), 
                  ', '.join(results.get('generated_files', [])[:3]) + ('...' if len(results.get('generated_files', [])) > 3 else ''))
    table.add_row("Total Time", f"{results.get('total_time', 0):.2f}s", results.get('time_details', ''))
    table.add_row("Deep Analysis", "✅ Enabled" if results.get('deep_analysis', False) else "❌ Disabled", 
                  results.get('deep_analysis_details', ''))
    
    console.print("\n")
    console.print(table)

def perform_analysis(deep: bool, targets: List[str], swagger_path: Optional[str] = None, user_message: Optional[str] = None) -> None:
    """Perform analysis based on targets with rich UI"""
    start_time = time.time()
    results = {
        'status': 'running',
        'generated_files': [],
        'generated_files_count': 0,
        'total_time': 0,
        'deep_analysis': deep,
        'status_details': '',
        'time_details': '',
        'deep_analysis_details': ''
    }
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False  # Keep progress visible
        ) as progress:
            
            analyzed_files_context = None
            
            # Perform deep analysis first if enabled
            if deep:
                task1 = progress.add_task("🔍 Deep analysis...", total=100)
                console.print(create_backend_step_panel(1, "Deep Analysis", "Analyzing project structure and dependencies"))
                
                # Update progress incrementally during deep analysis
                progress.update(task1, completed=10)
                analyzed_files_context = perform_deep_analysis(targets)
                progress.update(task1, completed=100)
                results['deep_analysis_details'] = f"Analyzed {len(analyzed_files_context.split(',')) if analyzed_files_context else 0} files"
            
            if "back" in targets:
                task2 = progress.add_task("⚙️  Generating tests...", total=100)
                console.print(create_backend_step_panel(2, "Test Generation", "Creating pytest tests from Swagger specification"))
                
                # Update progress incrementally
                progress.update(task2, completed=20)
                
                # Combine user message with analyzed files context
                final_message = user_message
                if analyzed_files_context:
                    final_message = f"{user_message or ''}\n\nDiscovered files:\n{analyzed_files_context}".strip()
                
                progress.update(task2, completed=50)
                test_results = write_tests(swagger_path, final_message)
                progress.update(task2, completed=100)
                results.update(test_results)
            
            if "ui" in targets:
                task3 = progress.add_task("🎨 UI analysis...", total=100)
                console.print(create_backend_step_panel(3, "UI Analysis", "Analyzing frontend components"))
                perform_ui_analysis()
                progress.update(task3, completed=100)
        
        results['total_time'] = time.time() - start_time
        results['time_details'] = f"Completed in {results['total_time']:.2f} seconds"
        
        # Display results
        if results['status'] == 'success':
            console.print(create_backend_step_panel(0, "✅ Analysis Complete", "All operations completed successfully", "success"))
        else:
            console.print(create_backend_step_panel(0, "❌ Analysis Failed", f"Error: {results.get('error', 'Unknown error')}", "failure"))
        
        print_backend_summary_table(results)
        
    except Exception as e:
        results['status'] = 'error'
        results['error'] = str(e)
        results['status_details'] = 'Failed with exception'
        results['total_time'] = time.time() - start_time
        
        console.print(create_backend_step_panel(0, "❌ Critical Error", f"Analysis failed: {e}", "failure"))
        print_backend_summary_table(results)
        raise

def write_tests(swagger_path: Optional[str] = None, user_message: Optional[str] = None) -> dict:
    """Write pytest tests from swagger specification"""
    try:
        from back import TestWriter
        
        if not swagger_path:
            raise ValueError("No swagger file path provided. Use --swagger argument.")
        
        console.print(f"📄 [cyan]Loading swagger file: {swagger_path}[/cyan]")
        
        # Load swagger JSON
        with open(swagger_path, 'r', encoding='utf-8') as f:
            swagger_data = json.load(f)
        
        console.print(f"✅ [green]Swagger file loaded successfully[/green]")
        
        writer = TestWriter()
        
        # Generate tests with user message
        console.print("🤖 [yellow]Generating tests with AI assistance...[/yellow]")
        result = writer.write_tests(swagger_data, user_message)
        
        if result["status"] == "success":
            console.print(f"✅ [green]Test generation completed successfully[/green]")
            console.print(f"📁 [cyan]Generated {len(result['generated_files'])} files[/cyan]")
            result['generated_files_count'] = len(result['generated_files'])
            result['status_details'] = 'Successfully generated all test files'
        else:
            console.print(f"❌ [red]Test generation failed: {result.get('error', 'Unknown error')}[/red]")
            result['status_details'] = f"Failed: {result.get('error', 'Unknown error')}"
        
        return result
        
    except ImportError as e:
        error_msg = f"Test generation dependencies not available: {e}"
        console.print(f"❌ [red]{error_msg}[/red]")
        return {"status": "error", "error": error_msg, "generated_files": [], "status_details": "Import error"}
    except Exception as e:
        error_msg = f"Test generation failed: {e}"
        console.print(f"❌ [red]{error_msg}[/red]")
        return {"status": "error", "error": error_msg, "generated_files": [], "status_details": "Execution error"}


def perform_deep_analysis(targets: List[str]) -> Optional[str]:
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
            
            # Return the analysis result for use in test generation
            return result.get('response', '')
        else:
            logger.info("OPENAI_API_KEY not set - skipping AI analysis, showing discovered files only")
            # Return basic file list when no AI analysis available
            return f"Project files discovered: {', '.join(files[:20])}"
        
    except Exception as e:
        logger.error(f"Deep analysis failed: {e}")
        return None


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