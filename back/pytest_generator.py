"""
Pytest test generator and file manager
"""
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from core.logging import get_logger

logger = get_logger("pytest_generator")


class PytestGenerator:
    """Generates and manages pytest test files"""
    
    def __init__(self, output_dir: str = "tests"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_tests(self, generated_content: str, filename: Optional[str] = None) -> List[str]:
        """Save generated tests to files"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_api_{timestamp}.py"
        
        if not filename.endswith('.py'):
            filename += '.py'
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(generated_content)
        
        logger.info(f"Saved test file: {filepath}")
        return [str(filepath)] 