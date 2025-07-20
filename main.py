"""
Unified QA Assistant - Main Entry Point

A command-line interface for analyzing both UI (frontend) and backend code.
Choose between frontend selector healing and backend test generation.
"""

import click
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
from rich.align import Align

console = Console()

def print_main_banner():
    """Display main application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║    ██████╗  █████╗      █████╗ ███████╗███████╗██╗███████╗████████╗     ║
    ║   ██╔═══██╗██╔══██╗    ██╔══██╗██╔════╝██╔════╝██║██╔════╝╚══██╔══╝     ║
    ║   ██║   ██║███████║    ███████║███████╗███████╗██║███████╗   ██║        ║
    ║   ██║▄▄ ██║██╔══██║    ██╔══██║╚════██║╚════██║██║╚════██║   ██║        ║
    ║   ╚██████╔╝██║  ██║    ██║  ██║███████║███████║██║███████║   ██║        ║
    ║    ╚══▀▀═╝ ╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚══════╝   ╚═╝        ║
    ║                                                                          ║
    ║                    🤖 Unified QA Testing Assistant                       ║
    ║                    ═══════════════════════════════════                   ║
    ║                                                                          ║
    ║              Frontend: AI-Powered Selector Healing                      ║
    ║              Backend: Swagger-Based Test Generation                      ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--back', is_flag=True, help='Backend mode: Generate pytest tests from API specs')
@click.option('--front', is_flag=True, help='Frontend mode: AI-Powered Selector Healing')
@click.option('--swagger', '--swagger-path', help='Path to swagger/OpenAPI JSON file')
@click.option('--message', '-m', help='Custom message/requirements for test generation')
@click.option('--deep', '--deep-analyze', is_flag=True, help='Enable deep analysis mode')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--interactive/--no-interactive', default=True, help='Enable interactive mode')
# Frontend specific options
@click.option('--v1-url', default='http://localhost:3000', help='URL for React V1 (original version)')
@click.option('--v2-url', default='http://localhost:3001', help='URL for React V2 (updated version)')
@click.option('--selectors-path', default='ui/page_selectors/page_v1.py', help='Path to selectors file')
@click.option('--test-path', default='ui/test/movie_app_tests.py', help='Path to test file')
@click.option('--dom-dir', default='ui/dom_snapshots', help='Directory for DOM snapshots')
@click.option('--reports-dir', default='ui/reports', help='Directory for reports')
@click.option('--confidence-threshold', default=0.5, type=float, help='Minimum confidence threshold for healing')
def cli(ctx, back, front, swagger, message, deep, verbose, interactive, v1_url, v2_url, selectors_path, test_path, dom_dir, reports_dir, confidence_threshold):
    """🤖 Unified QA Assistant - Choose between Frontend and Backend testing"""
    
    # Handle legacy flag format
    if back or front:
        if back and front:
            console.print("❌ [red]Cannot specify both --back and --front flags[/red]")
            sys.exit(1)
        
        if back:
            # Call backend functionality directly
            ctx.invoke(backend_legacy, swagger=swagger, message=message, deep=deep, verbose=verbose, interactive=interactive)
            return
        
        if front:
            # Call frontend functionality directly  
            ctx.invoke(frontend_legacy, v1_url=v1_url, v2_url=v2_url, selectors_path=selectors_path, test_path=test_path, 
                      dom_dir=dom_dir, reports_dir=reports_dir, interactive=interactive, confidence_threshold=confidence_threshold)
            return
    
    # If no subcommand and no legacy flags, show main interface
    if ctx.invoked_subcommand is None:
        print_main_banner()
        
        console.print("\n[bold cyan]Welcome to the Unified QA Testing Assistant![/bold cyan]")
        console.print("\nChoose your testing focus:\n")
        
        # Create options table
        table = Table(box=box.ROUNDED, show_header=False)
        table.add_column("Option", style="bold cyan", width=15)
        table.add_column("Description", style="white", width=50)
        table.add_column("Use Case", style="dim", width=25)
        
        table.add_row(
            "frontend", 
            "🎨 AI-Powered Selector Healing\nFix broken UI test selectors automatically", 
            "UI/Frontend Testing"
        )
        table.add_row(
            "backend", 
            "⚙️  Swagger-Based Test Generation\nGenerate pytest tests from API specs", 
            "API/Backend Testing"
        )
        
        console.print(table)
        console.print("\n[dim]Usage Options:[/dim]")
        console.print("[dim]• Subcommands: python main.py [frontend|backend] --help[/dim]")
        console.print("[dim]• Legacy flags: python main.py --back --swagger file.json --message \"...\" --deep[/dim]")
        console.print("[dim]• Legacy flags: python main.py --front --v1-url http://localhost:3000[/dim]\n")

def backend_legacy(swagger, message, deep, verbose, interactive):
    """Backend functionality for legacy flag format"""
    print_main_banner()
    console.print("\n[bold blue]⚙️ BACKEND MODE: Swagger-Based Test Generation[/bold blue]\n")
    
    if not swagger:
        console.print("❌ [red]Error: --swagger option is required for backend mode[/red]")
        console.print("💡 [yellow]Usage: python main.py --back --swagger path/to/swagger.json[/yellow]")
        sys.exit(1)
    
    # Import and run the backend functionality
    try:
        from cli.cli import perform_analysis
        from core.logging import setup_logging
        
        setup_logging(verbose)
        
        if interactive:
            console.print("[bold]Configuration Summary:[/bold]")
            table = Table(box=box.SIMPLE)
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Swagger File", swagger)
            table.add_row("Deep Analysis", "✅ Enabled" if deep else "❌ Disabled")
            table.add_row("Custom Message", message or "None")
            table.add_row("Verbose Output", "✅ Enabled" if verbose else "❌ Disabled")
            
            console.print(table)
            
            if not Confirm.ask("\nProceed with test generation?"):
                console.print("❌ [red]Aborted by user[/red]")
                return
        
        # Run backend analysis
        console.print("\n" + "═" * 70)
        console.print(Align.center("[bold blue]⚙️ INITIATING BACKEND TEST GENERATION ⚙️[/bold blue]"))
        console.print("═" * 70 + "\n")
        
        targets = ["back"]
        perform_analysis(deep, targets, swagger, message)
        
        console.print("\n" + "═" * 70)
        console.print(Align.center("🎉 [bold green]BACKEND ANALYSIS COMPLETED![/bold green] 🎉"))
        console.print("═" * 70)
        
    except ImportError as e:
        console.print(f"❌ [red]Backend dependencies not available: {e}[/red]")
        console.print("💡 [yellow]Make sure to install: pip install -r requirements.txt[/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Backend analysis failed: {e}[/red]")

def frontend_legacy(v1_url, v2_url, selectors_path, test_path, dom_dir, reports_dir, interactive, confidence_threshold):
    """Frontend functionality for legacy flag format"""
    print_main_banner()
    console.print("\n[bold green]🎨 FRONTEND MODE: AI-Powered Selector Healing[/bold green]\n")
    
    console.print("🚀 [cyan]Starting AI-Powered Selector Healing Demo...[/cyan]")
    console.print("📋 [dim]This will automatically run the complete healing process[/dim]\n")
    
    # Change to ui directory and run the demo
    try:
        import subprocess
        import os
        
        # Change to ui directory and run demo
        original_cwd = os.getcwd()
        os.chdir("ui")
        
        console.print("▶️  [yellow]Executing: python run_demo.py[/yellow]")
        
        # Run the demo script
        result = subprocess.run([sys.executable, "run_demo.py"], 
                              capture_output=False, 
                              text=True, 
                              check=False)
        
        # Return to original directory
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            console.print("\n🎉 [bold green]Frontend demo completed successfully![/bold green]")
        else:
            console.print(f"\n💔 [bold red]Frontend demo failed with exit code: {result.returncode}[/bold red]")
        
    except Exception as e:
        console.print(f"❌ [red]Error running frontend demo: {e}[/red]")
        if 'original_cwd' in locals():
            os.chdir(original_cwd)

@cli.command()
@click.option('--v1-url', default='http://localhost:3000', help='URL for React V1 (original version)')
@click.option('--v2-url', default='http://localhost:3001', help='URL for React V2 (updated version)')
@click.option('--selectors-path', default='ui/page_selectors/page_v1.py', help='Path to selectors file')
@click.option('--test-path', default='ui/test/movie_app_tests.py', help='Path to test file')
@click.option('--dom-dir', default='ui/dom_snapshots', help='Directory for DOM snapshots')
@click.option('--reports-dir', default='ui/reports', help='Directory for reports')
@click.option('--interactive/--no-interactive', default=True, help='Enable interactive mode')
@click.option('--confidence-threshold', default=0.5, type=float, help='Minimum confidence threshold for healing')
def frontend(v1_url, v2_url, selectors_path, test_path, dom_dir, reports_dir, interactive, confidence_threshold):
    """🎨 Frontend: AI-Powered Selector Healing - Fix broken UI test selectors automatically"""
    print_main_banner()
    console.print("\n[bold green]🎨 FRONTEND MODE: AI-Powered Selector Healing[/bold green]\n")
    
    console.print("🚀 [cyan]Starting AI-Powered Selector Healing Demo...[/cyan]")
    console.print("📋 [dim]This will automatically run the complete healing process[/dim]\n")
    
    # Change to ui directory and run the demo
    try:
        import subprocess
        import os
        
        # Change to ui directory and run demo
        original_cwd = os.getcwd()
        os.chdir("ui")
        
        console.print("▶️  [yellow]Executing: python run_demo.py[/yellow]")
        
        # Run the demo script
        result = subprocess.run([sys.executable, "run_demo.py"], 
                              capture_output=False, 
                              text=True, 
                              check=False)
        
        # Return to original directory
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            console.print("\n🎉 [bold green]Frontend demo completed successfully![/bold green]")
        else:
            console.print(f"\n💔 [bold red]Frontend demo failed with exit code: {result.returncode}[/bold red]")
        
    except Exception as e:
        console.print(f"❌ [red]Error running frontend demo: {e}[/red]")
        if 'original_cwd' in locals():
            os.chdir(original_cwd)

@cli.command()
@click.option('--swagger', '--swagger-path', required=True, help='Path to swagger/OpenAPI JSON file')
@click.option('--message', '-m', help='Custom message/requirements for test generation')
@click.option('--deep', '--deep-analyze', is_flag=True, help='Enable deep analysis mode')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--interactive/--no-interactive', default=True, help='Enable interactive mode')
def backend(swagger, message, deep, verbose, interactive):
    """⚙️ Backend: Swagger-Based Test Generation - Generate pytest tests from API specifications"""
    backend_legacy(swagger, message, deep, verbose, interactive)

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n\n👋 [yellow]Goodbye! Process interrupted.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error: {e}[/red]")
        sys.exit(1) 