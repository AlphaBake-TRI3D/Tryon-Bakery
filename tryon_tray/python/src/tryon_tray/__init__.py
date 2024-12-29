"""A unified interface for virtual try-on services"""

__version__ = "0.1.0"

# Import services to ensure registration
from . import services
from .services import video  # Video generation services
from .services import vton   # Virtual try-on services 