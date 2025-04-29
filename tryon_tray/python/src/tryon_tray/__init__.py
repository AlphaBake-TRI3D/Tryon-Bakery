"""A unified interface for virtual try-on services"""

__version__ = "0.2.2"

# Import services to ensure registration
from . import services
from .services import video  # Video generation services
from .services import vton   # Virtual try-on services

# Import the main API function
from .vton_api import VTON

# Import utility functions for model discovery
from .utils.discovery import get_available_models, get_model_params, get_model_sample_config

# Export public API
__all__ = [
    'VTON',
    'get_available_models',
    'get_model_params', 
    'get_model_sample_config'
] 