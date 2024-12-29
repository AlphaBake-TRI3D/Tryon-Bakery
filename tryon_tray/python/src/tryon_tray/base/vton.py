"""Base class for virtual try-on services."""

from abc import abstractmethod
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
import time
import requests

from .service import BaseService
from ..utils.file_io import download_file

class BaseVTON(BaseService):
    """Base class for virtual try-on services."""
    
    def __init__(
        self,
        model_image: str,
        garment_image: str,
        auto_download: bool = False,
        download_path: Optional[str] = None,
        show_polling_progress: bool = False,
        **kwargs
    ):
        """Initialize virtual try-on service.
        
        Args:
            model_image: Path to the model/person image
            garment_image: Path to the garment image
            auto_download: Whether to automatically download the result
            download_path: Path to save the downloaded image
            show_polling_progress: Whether to show polling progress
            **kwargs: Additional service-specific parameters
        """
        super().__init__(**kwargs)
        self.model_image = model_image
        self.garment_image = garment_image
        self.auto_download = auto_download
        self.download_path = download_path
        self.show_polling_progress = show_polling_progress
        self.result_urls: List[str] = []
        self.params = kwargs
        
    def _print_polling_progress(self):
        """Print polling progress if enabled."""
        if self.show_polling_progress:
            print(".", end="", flush=True)
    
    def _download_result(self) -> str:
        """Download the generated image."""
        if not self.result_urls:
            raise ValueError("No result URLs available")
            
        if not self.download_path:
            raise ValueError("No download path specified")
            
        # Ensure directory exists
        Path(self.download_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Download the first result
        download_file(self.result_urls[0], self.download_path)
        return self.download_path
    
    def run_and_wait(
        self,
        max_attempts: int = 60,
        delay: int = 5
    ) -> List[str]:
        """Run the try-on process and wait for completion.
        
        Args:
            max_attempts: Maximum number of polling attempts
            delay: Time between polling attempts in seconds
            
        Returns:
            List of result URLs
        """
        # Start the job
        self.run()
        
        # Poll for results
        if self.show_polling_progress:
            print("\nPolling for results", end="", flush=True)
            
        for _ in range(max_attempts):
            self._print_polling_progress()
            
            is_complete, result = self.check_status()
            if is_complete:
                if isinstance(result, Exception):
                    raise result
                if self.auto_download and self.download_path:
                    self._download_result()
                return result
            
            time.sleep(delay)
        
        raise TimeoutError("Maximum polling attempts reached")
    
    @abstractmethod
    def run(self) -> str:
        """Start the try-on process and return job ID."""
        pass
    
    @abstractmethod
    def check_status(self) -> Tuple[bool, Optional[Union[List[str], Exception]]]:
        """Check current status of the try-on job.
        
        Returns:
            Tuple containing:
            - bool: Whether the job is complete
            - Optional[Union[List[str], Exception]]: Result URLs or error
        """
        pass
    
    @abstractmethod
    def get_result(self) -> Dict[str, Any]:
        """Get the try-on result."""
        pass 