"""
OpenAI client wrapper for generating pytest tests
"""
import json
from typing import Dict, Any, Optional
from openai import OpenAI

from core.logging import get_logger
from core.prompts import SYSTEM_PROMPT, FUNCTION_SCHEMA
from .config import BackendConfig

logger = get_logger("openai_client")


class OpenAIClient:
    """OpenAI client for generating pytest tests"""
    
    def __init__(self, config: BackendConfig):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
    
    def generate_pytest_tests(self, swagger_data: Dict[str, Any], user_message: Optional[str] = None) -> str:
        """Generate pytest tests from swagger data"""
        try:
            logger.info("Sending request to OpenAI for pytest generation")
            
            # Convert swagger data to JSON string
            swagger_json = json.dumps(swagger_data, indent=2)
            
            # Combine user message with swagger JSON
            if user_message:
                content = f"{user_message}\n\nHere is my swagger:\n{swagger_json}"
            else:
                content = f"Here is my swagger:\n{swagger_json}"
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user", 
                        "content": content
                    }
                ],
                functions=[FUNCTION_SCHEMA],
                function_call={"name": "generate_pytest_tests"},
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            # Extract function call result
            function_call = response.choices[0].message.function_call
            result = json.loads(function_call.arguments)
            
            logger.info("Successfully generated pytest tests")
            return result["code"]
            
        except Exception as e:
            logger.error(f"Error generating tests with OpenAI: {e}")
            raise 