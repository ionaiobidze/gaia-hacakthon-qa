import logging
from rich.logging import RichHandler
from rich.console import Console

console = Console()

def setup_logging(verbose: bool) -> None:
    """Configure logging for the application with Rich integration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Use Rich handler for better formatting
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True
    )
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[rich_handler]
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name) 