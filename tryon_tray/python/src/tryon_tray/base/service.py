"""Base class for all services."""

from abc import ABC
from typing import Dict, Any

class BaseService(ABC):
    """Base class for all services."""
    
    def __init__(self, **kwargs):
        """Initialize service with optional parameters."""
        self.api_key = kwargs.get("api_key")
        self.result_data = None
    
    def get_result(self) -> Dict[str, Any]:
        """Get operation results."""
        if not self.result_data:
            raise ValueError("No result available. Run the operation first.")
        return self.result_data 