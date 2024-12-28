from abc import ABC, abstractmethod
import time
from datetime import datetime

class BaseVTON(ABC):
    def __init__(self, model_image, garment_image, **kwargs):
        self.model_image = model_image
        self.garment_image = garment_image
        self.api_key = kwargs.get("api_key")
        self.status = "initialized"
        self.prediction_id = None
        self.result_data = None
        self.params = kwargs
        # Add timing attributes
        self.start_time = None
        self.end_time = None
        self.time_taken = None
        # Add polling progress attribute
        self.show_polling_progress = kwargs.get("show_polling_progress", False)
        self._polling_start = None

    @abstractmethod
    def run(self):
        """Kick off the ML job. Return a job/prediction ID or store it internally."""
        pass

    @abstractmethod
    def check_status(self):
        """
        Check current status of the job.
        Returns:
            tuple: (is_completed, result_or_error)
            - is_completed: bool indicating if job is done (success or failure)
            - result_or_error: result data if successful, error message if failed
        """
        pass

    def _print_polling_progress(self):
        """Print polling progress if enabled"""
        if self.show_polling_progress and self._polling_start:
            elapsed = time.time() - self._polling_start
            print(f"Polling... {elapsed:.1f}s", end='\r')

    def poll(self, max_attempts=60, delay=5):
        """Generic polling implementation that all services can use"""
        for attempt in range(max_attempts):
            self._print_polling_progress()
            
            try:
                is_completed, result_or_error = self.check_status()
                
                if is_completed:
                    if isinstance(result_or_error, Exception):
                        self.status = "failed"
                        raise result_or_error
                    else:
                        self.status = "completed"
                        self.result_data = result_or_error
                        return self.result_data
                
                time.sleep(delay)
                
            except Exception as e:
                self.status = "failed"
                raise e
        
        self.status = "timeout"
        raise TimeoutError(f"{self.__class__.__name__} polling timed out")

    def run_and_wait(self, max_attempts=60, delay=5):
        """Convenience method to do run + poll in one go."""
        self.start_time = datetime.now()
        self.run()
        
        # Track polling time
        self._polling_start = time.time()
        result = self.poll(max_attempts, delay)
        if self.show_polling_progress:
            polling_time = time.time() - self._polling_start
            print(f"\nPolling completed after {polling_time:.1f} seconds")
            
        self.end_time = datetime.now()
        self.time_taken = self.end_time - self.start_time
        return result 