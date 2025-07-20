import click
import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Optional, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box
from rich.layout import Layout
from rich.align import Align

# Import your existing modules
from .runner.server_launcher import ReactServerManager
from .runner.dom_fetcher import DOMFetcher
from .agents.selector_agent import SelectorAgent
from .runner.selector_updater import SelectorUpdater

console = Console()

# ═══════════════════════════════════════════════════════════════════════════════
#                                   CLI STYLING
# ═══════════════════════════════════════════════════════════════════════════════

def print_banner():
    """Display elegant ASCII banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║    █████╗ ██╗      ███████╗███████╗██╗     ███████╗ ██████╗████████╗    ║
    ║   ██╔══██╗██║      ██╔════╝██╔════╝██║     ██╔════╝██╔════╝╚══██╔══╝    ║
    ║   ███████║██║█████╗███████╗█████╗  ██║     █████╗  ██║        ██║       ║
    ║   ██╔══██║██║╚════╝╚════██║██╔══╝  ██║     ██╔══╝  ██║        ██║       ║
    ║   ██║  ██║██║      ███████║███████╗███████╗███████╗╚██████╗   ██║       ║
    ║   ╚═╝  ╚═╝╚═╝      ╚══════╝╚══════╝╚══════╝╚══════╝ ╚═════╝   ╚═╝       ║
    ║                                                                          ║
    ║                    🤖 AI-Powered Selector Healing Tool                   ║
    ║                    ═══════════════════════════════════════               ║
    ║                                                                          ║
    ║              Eliminates broken UI tests caused by outdated              ║
    ║                        CSS selectors automatically                       ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

def create_step_panel(step_num: int, title: str, description: str, status: str = "running"):
    """Create a beautiful step panel"""
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

def print_summary_table(results: Dict):
    """Display elegant results summary"""
    table = Table(
        title="🎯 Healing Summary",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Value", style="green", width=15)
    table.add_column("Details", style="white", width=30)
    
    table.add_row("Success Rate", f"{results.get('success_rate', 0)}%", results.get('success_details', ''))
    table.add_row("Selectors Healed", str(results.get('healed_count', 0)), results.get('healed_details', ''))
    table.add_row("Total Time", f"{results.get('total_time', 0):.2f}s", results.get('time_details', ''))
    table.add_row("Confidence", f"{results.get('confidence', 0):.2f}", results.get('confidence_details', ''))
    
    console.print("\n")
    console.print(table)

# ═══════════════════════════════════════════════════════════════════════════════
#                                 CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class HealingOrchestrator:
    """Main orchestrator class with enhanced CLI integration"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.server_manager = ReactServerManager()
        self.results = {
            'success_rate': 0,
            'healed_count': 0,
            'total_time': 0,
            'confidence': 0
        }
        
    def run_healing_process(self) -> bool:
        """Run the complete healing process with beautiful progress display"""
        start_time = time.time()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console,
                transient=False  # Keep progress visible
            ) as progress:
                
                # Step 1: Server Setup
                task1 = progress.add_task("🚀 Starting servers...", total=100)
                console.print("\n")
                console.print(create_step_panel(1, "Server Setup", "Initializing React V1 and V2 environments"))
                
                progress.update(task1, completed=20)
                if not self._start_servers():
                    console.print("❌ [red]Failed to start servers[/red]")
                    return False
                progress.update(task1, completed=100)
                
                # Step 2: Baseline Tests
                task2 = progress.add_task("✅ Running baseline tests...", total=100)
                console.print("\n")
                console.print(create_step_panel(2, "Baseline Validation", "Confirming tests pass on original version"))
                
                progress.update(task2, completed=30)
                if not self._run_baseline_tests():
                    console.print("❌ [red]Baseline tests failed[/red]")
                    return False
                progress.update(task2, completed=100)
                
                # Step 3: Failure Detection
                task3 = progress.add_task("❌ Detecting failures...", total=100)
                console.print("\n")
                console.print(create_step_panel(3, "Failure Detection", "Identifying broken selectors in new version"))
                
                progress.update(task3, completed=25)
                if not self._detect_failures():
                    console.print("❌ [red]Failure detection unsuccessful[/red]")
                    return False
                progress.update(task3, completed=100)
                
                # Step 4: DOM Analysis
                task4 = progress.add_task("📄 Analyzing DOM structures...", total=100)
                console.print("\n")

                console.print(create_step_panel(4, "DOM Analysis", "Capturing and comparing DOM structures"))
                
                progress.update(task4, completed=40)
                dom_data = self._fetch_dom_data()
                if not dom_data:
                    console.print("❌ [red]DOM analysis failed[/red]")
                    return False
                progress.update(task4, completed=100)
                
                # Step 5: AI Healing
                task5 = progress.add_task("🤖 AI-powered healing...", total=100)
                console.print("\n")
                console.print(create_step_panel(5, "AI-Powered Mapping", "Using GPT-4 to map old selectors to new ones"))
                
                progress.update(task5, completed=30)
                healing_success = self._perform_healing(dom_data)
                if not healing_success:
                    console.print("❌ [red]AI healing failed[/red]")
                    return False
                progress.update(task5, completed=100)
                
                # Step 6: Validation
                task6 = progress.add_task("✅ Validating fixes...", total=100)
                console.print("\n")
                console.print(create_step_panel(6, "Validation & Testing", "Confirming healed selectors work correctly"))
                
                progress.update(task6, completed=50)
                final_success = self._validate_healing()
                progress.update(task6, completed=100)
                
                self.results['total_time'] = time.time() - start_time
                return final_success
                
        except Exception as e:
            console.print(f"❌ [red]Critical error: {e}[/red]")
            return False
        finally:
            self._cleanup()
    
    def _start_servers(self) -> bool:
        """Start React servers"""
        return self.server_manager.start_all_servers()
    
    def _run_baseline_tests(self) -> bool:
        """Run baseline tests on V1"""
        os.environ['TEST_URL'] = self.config['react_v1_url']
        os.environ['SELECTOR_MODULE'] = "page_selectors.page_v1"
        return self._run_command([sys.executable, "-m", self.config['test_module']])
    
    def _detect_failures(self) -> bool:
        """Detect failures on V2"""
        os.environ['TEST_URL'] = self.config['react_v2_url']
        return not self._run_command([sys.executable, "-m", self.config['test_module']])
    
    def _fetch_dom_data(self) -> Optional[Dict]:
        """Fetch DOM data from both versions"""
        try:
            with DOMFetcher() as fetcher_v1:
                dom_v1 = fetcher_v1.fetch_dom(self.config['react_v1_url'])
                
            with DOMFetcher() as fetcher_v2:
                dom_v2 = fetcher_v2.fetch_dom(self.config['react_v2_url'])
                
            if dom_v1.get("success") and dom_v2.get("success"):
                return {"dom_v1": dom_v1, "dom_v2": dom_v2}
        except Exception as e:
            console.print(f"DOM fetch error: {e}")
        return None
    
    def _perform_healing(self, dom_data: Dict) -> bool:
        """Perform AI-powered healing"""
        api_key = os.environ.get("OPENAI_API_KEY")
        agent = SelectorAgent(api_key=api_key)
        updater = SelectorUpdater()
        
        # Get selectors to map
        from .page_selectors import page_v1
        selectors_to_map = self._get_selectors_from_module(page_v1)
        
        # Perform mapping
        mapping_results = agent.batch_map_selectors(
            selectors_to_map, 
            dom_data["dom_v1"]["html"], 
            dom_data["dom_v2"]["html"]
        )
        
        # Apply updates
        updates_info = updater.batch_update_from_mapping(
            self.config['selectors_path'], 
            mapping_results, 
            create_new_version=True
        )
        
        self.results['healed_count'] = updates_info.get('updates_applied', 0)
        return updates_info.get('updates_applied', 0) > 0
    
    def _validate_healing(self) -> bool:
        """Validate that healing worked"""
        os.environ['SELECTOR_MODULE'] = "page_selectors.page_v2"
        return self._run_command([sys.executable, "-m", self.config['test_module']])
    
    def _run_command(self, command) -> bool:
        """Run a command and return success status"""
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=180)
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_selectors_from_module(self, module):
        """Extract selectors from module"""
        import inspect
        selectors = {}
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if name == 'Locators':
                for loc_name, loc_val in inspect.getmembers(cls):
                    if not loc_name.startswith('__') and isinstance(loc_val, tuple):
                        selectors[loc_name] = loc_val[1]
        return selectors
    
    def _cleanup(self):
        """Clean up resources"""
        self.server_manager.stop_all_servers()

# ═══════════════════════════════════════════════════════════════════════════════
#                                 CLI COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """AI-Powered Selector Healing Tool - Eliminate broken UI tests automatically"""
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print("\n[bold cyan]Welcome to the AI-Powered Selector Healing Tool![/bold cyan]")
        console.print("\nUse [bold]--help[/bold] to see available commands, or run [bold]heal[/bold] to start the healing process.\n")

@cli.command()
@click.option('--v1-url', default='http://localhost:3000', help='URL for React V1 (original version)')
@click.option('--v2-url', default='http://localhost:3001', help='URL for React V2 (updated version)')
@click.option('--selectors-path', default='page_selectors/page_v1.py', help='Path to selectors file')
@click.option('--test-path', default='test/movie_app_tests.py', help='Path to test file')
@click.option('--dom-dir', default='dom_snapshots', help='Directory for DOM snapshots')
@click.option('--reports-dir', default='reports', help='Directory for reports')
@click.option('--interactive/--no-interactive', default=True, help='Enable interactive mode')
@click.option('--confidence-threshold', default=0.5, type=float, help='Minimum confidence threshold for healing')
def heal(v1_url, v2_url, selectors_path, test_path, dom_dir, reports_dir, interactive, confidence_threshold):
    """🚀 Start the automated selector healing process"""
    
    print_banner()
    
    # Verify API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        console.print("⚠️  [yellow]WARNING: OPENAI_API_KEY not set. Using rule-based fallback.[/yellow]")
        if interactive and not Confirm.ask("Continue without AI assistance?"):
            console.print("❌ [red]Aborted by user[/red]")
            return
    else:
        console.print("✅ [green]OPENAI_API_KEY found. AI agent will be used.[/green]")
    
    # Create directories
    Path(dom_dir).mkdir(exist_ok=True)
    Path(reports_dir).mkdir(exist_ok=True)
    
    # Configuration
    config = {
        'react_v1_url': v1_url,
        'react_v2_url': v2_url,
        'selectors_path': selectors_path,
        'test_module': test_path.replace(".py", "").replace(os.path.sep, "."),
        'dom_dir': dom_dir,
        'reports_dir': reports_dir,
        'confidence_threshold': confidence_threshold
    }
    
    if interactive:
        console.print("\n[bold]Configuration Summary:[/bold]")
        table = Table(box=box.SIMPLE)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("V1 URL", config['react_v1_url'])
        table.add_row("V2 URL", config['react_v2_url'])
        table.add_row("Selectors Path", config['selectors_path'])
        table.add_row("Test Module", config['test_module'])
        table.add_row("Confidence Threshold", f"{config['confidence_threshold']}")
        
        console.print(table)
        
        if not Confirm.ask("\nProceed with healing?"):
            console.print("❌ [red]Aborted by user[/red]")
            return
    
    # Run healing process
    console.print("\n" + "═" * 70)
    console.print(Align.center("[bold cyan]🤖 INITIATING AI-POWERED HEALING SEQUENCE 🤖[/bold cyan]"))
    console.print("═" * 70 + "\n")
    
    orchestrator = HealingOrchestrator(config)
    success = orchestrator.run_healing_process()
    
    # Display results
    console.print("\n" + "═" * 70)
    if success:
        console.print(Align.center("🎉 [bold green]HEALING COMPLETED SUCCESSFULLY![/bold green] 🎉"))
        orchestrator.results['success_rate'] = 100
    else:
        console.print(Align.center("💔 [bold red]HEALING FAILED[/bold red] 💔"))
        orchestrator.results['success_rate'] = 0
    
    console.print("═" * 70)
    print_summary_table(orchestrator.results)
    console.print("\n")

@cli.command()
def status():
    """📊 Check the status of React servers and environment"""
    print_banner()
    
    console.print("[bold]Environment Status Check[/bold]\n")
    
    # Check API key
    api_key = os.environ.get("OPENAI_API_KEY")
    api_status = "✅ Available" if api_key else "❌ Not Set"
    
    # Check server connectivity
    import requests
    try:
        v1_response = requests.get("http://localhost:3000", timeout=5)
        v1_status = "✅ Running" if v1_response.status_code == 200 else "❌ Error"
    except:
        v1_status = "❌ Not Running"
    
    try:
        v2_response = requests.get("http://localhost:3001", timeout=5)
        v2_status = "✅ Running" if v2_response.status_code == 200 else "❌ Error"
    except:
        v2_status = "❌ Not Running"
    
    # Status table
    table = Table(title="🔍 System Status", box=box.ROUNDED)
    table.add_column("Component", style="cyan", width=20)
    table.add_column("Status", style="white", width=15)
    table.add_column("Details", style="white", width=30)
    
    table.add_row("OpenAI API Key", api_status, "Required for AI-powered healing")
    table.add_row("React V1 Server", v1_status, "http://localhost:3000")
    table.add_row("React V2 Server", v2_status, "http://localhost:3001")
    
    console.print(table)

@cli.command()
def config():
    """⚙️  Interactive configuration setup"""
    print_banner()
    
    console.print("[bold]Interactive Configuration Setup[/bold]\n")
    
    # Get configuration values
    v1_url = Prompt.ask("React V1 URL", default="http://localhost:3000")
    v2_url = Prompt.ask("React V2 URL", default="http://localhost:3001")
    selectors_path = Prompt.ask("Selectors file path", default="page_selectors/page_v1.py")
    test_path = Prompt.ask("Test file path", default="test/movie_app_tests.py")
    
    # Save to config file
    config_data = {
        "react_v1_url": v1_url,
        "react_v2_url": v2_url,
        "selectors_path": selectors_path,
        "test_path": test_path,
        "dom_dir": "dom_snapshots",
        "reports_dir": "reports"
    }
    
    config_file = Path("selector_healing_config.json")
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    console.print(f"\n✅ [green]Configuration saved to {config_file}[/green]")

@cli.command()
def demo():
    """🎬 Run a quick demonstration of the healing process"""
    print_banner()
    
    console.print("[bold cyan]🎬 Demo Mode - Quick Healing Demonstration[/bold cyan]\n")
    
    # Run with demo settings
    config = {
        'react_v1_url': 'http://localhost:3000',
        'react_v2_url': 'http://localhost:3001',
        'selectors_path': 'page_selectors/page_v1.py',
        'test_module': 'test.movie_app_tests',
        'dom_dir': 'dom_snapshots',
        'reports_dir': 'reports',
        'confidence_threshold': 0.5
    }
    
    orchestrator = HealingOrchestrator(config)
    success = orchestrator.run_healing_process()
    
    if success:
        console.print("\n🎉 [bold green]Demo completed successfully![/bold green]")
    else:
        console.print("\n💔 [bold red]Demo encountered issues[/bold red]")

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n\n👋 [yellow]Goodbye! Healing process interrupted.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error: {e}[/red]")
        sys.exit(1)