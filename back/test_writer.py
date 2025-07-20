"""
Test writer that generates pytest tests from swagger specifications
"""
from typing import Optional, Dict, Any, List
import json

from core.logging import get_logger
from .config import BackendConfig
from .openai_client import OpenAIClient
from .pytest_generator import PytestGenerator

logger = get_logger("test_writer")


class TestWriter:
    """Main test writer class for generating pytest tests from swagger"""
    
    def __init__(self, config: Optional[BackendConfig] = None):
        self.config = config or BackendConfig.from_env()
        
        self.openai_client = OpenAIClient(self.config)
        self.pytest_generator = PytestGenerator(self.config.output_dir)
        
        logger.info("Test writer initialized")
    
    def write_tests(self, swagger_data: Dict[str, Any], user_message: Optional[str] = None) -> Dict[str, Any]:
        """Main test writing method"""
        try:
            logger.info("Starting test generation")
            
            generated_tests = self.openai_client.generate_pytest_tests(swagger_data, user_message)
            
            test_files = self.pytest_generator.save_tests(generated_tests)
            
            result = {
                "status": "success",
                "generated_files": test_files
            }
            
            logger.info(f"Test generation completed successfully. Generated {len(test_files)} test files.")
            return result
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            } 