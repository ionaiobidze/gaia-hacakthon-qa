from typing import Dict, Any
from abc import ABC, abstractmethod

class Tool(ABC):
    @abstractmethod
    def execute(self, args: Dict) -> Any: pass
    @abstractmethod
    def schema(self) -> Dict: pass
