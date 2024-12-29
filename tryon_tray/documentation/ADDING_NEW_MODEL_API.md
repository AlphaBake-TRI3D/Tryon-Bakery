# Adding a New Model API to Tryon-Tray

This guide demonstrates how to add a new virtual try-on model API to the Tryon-Tray codebase, using VModel API as an example.

## Installation and Setup

1. Install the package in development mode:
```bash
# From the root directory of the project
pip install -e tryon_tray/python
```

2. Set up environment variables in `.env`:
```bash
VMODEL_API_KEY=your_api_key_here
```

## Configuration and Environment Setup

1. Create a `.env` file in the `examples` directory:
```bash
# tryon_tray/examples/.env
VMODEL_API_KEY=your_api_key_here
```

2. For development, you can also place the `.env` file in the root directory:
```bash
# .env in project root
VMODEL_API_KEY=your_api_key_here
```

Note: The example scripts are configured to look for the `.env` file in the `examples` directory first.

## Directory Structure

When adding a new model API, you need to add or modify files in these locations:

```
tryon_tray/python/src/tryon_tray/
├── api/
│   └── vmodel.py           # API client implementation
├── services/vton/
│   ├── __init__.py        # Service registration
│   └── vmodel.py          # Service implementation
├── utils/
│   └── config.py          # Configuration utilities
└── examples/
    └── vmodel_example.py  # Example usage
```

## Directory Structure for Examples

```
tryon_tray/examples/
├── .env                  # Environment variables
├── inputs/
│   ├── person.jpg       # Model image
│   └── garment.jpeg     # Garment image
├── outputs/             # Generated results
└── vmodel_example.py    # Example script
```

## Step-by-Step Implementation

### 1. API Client Implementation (api/vmodel.py)

```python
"""VModel API client implementation."""

import os
import time
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path

class VModelAPIClient:
    """Client for interacting with the VModel API."""
    
    BASE_URL = "https://developer.vmodel.ai/api/vmodel/v1/ai-virtual-try-on"
    
    def __init__(self, api_key: str):
        """Initialize the VModel API client."""
        self.api_key = api_key
        self.headers = {
            "Authorization": api_key,
            "accept": "application/json"
        }
    
    def create_job(
        self,
        model_image_path: str,
        garment_image_path: str,
        clothes_type: str = "upper_body",
        prompt: str = ""
    ) -> str:
        """Create a virtual try-on job."""
        files = [
            ('clothes_image', (os.path.basename(garment_image_path), open(garment_image_path, 'rb'), 'image/png')),
            ('custom_model', (os.path.basename(model_image_path), open(model_image_path, 'rb'), 'image/png'))
        ]
        
        payload = {
            'clothes_type': clothes_type,
            'prompt': prompt
        }
        
        response = requests.post(
            f"{self.BASE_URL}/create-job",
            headers=self.headers,
            data=payload,
            files=files
        )
        response.raise_for_status()
        
        return response.json()["result"]["job_id"]
    
    def fetch_job(
        self,
        job_id: str,
        max_attempts: int = 60,
        delay: int = 5
    ) -> List[str]:
        """Fetch the job status and results."""
        for _ in range(max_attempts):
            response = requests.get(
                f"{self.BASE_URL}/get-job/{job_id}",
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            if result["code"] == 100000 and result["result"]["output_image_url"]:
                return result["result"]["output_image_url"]
            elif result["code"] == 300104:
                raise Exception("Image generation failed.")
            
            time.sleep(delay)
        
        raise TimeoutError("Maximum polling attempts reached")
    
    def download_image(self, url: str, output_path: str) -> None:
        """Download the generated image."""
        response = requests.get(url)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
```

### 2. Service Implementation (services/vton/vmodel.py)

```python
"""VModel virtual try-on service."""

import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, Union, List

from ...base.vton import BaseVTON
from ...api.vmodel import VModelAPIClient
from ...utils.config import get_vmodel_api_token

class VModelVTON(BaseVTON):
    """VModel virtual try-on service implementation."""
    
    def __init__(self, model_image: str, garment_image: str, **kwargs):
        """Initialize VModel VTON service."""
        super().__init__(model_image, garment_image, **kwargs)
        if not self.api_key:
            self.api_key = get_vmodel_api_token()
        self.client = VModelAPIClient(api_key=self.api_key)
        self._job_id = None
        self.start_time = None
        self.end_time = None
        self.time_taken = None
        
    def run(self) -> str:
        """Run the try-on process."""
        # Validate image paths
        if not os.path.exists(self.model_image):
            raise ValueError(f"Model image not found: {self.model_image}")
        if not os.path.exists(self.garment_image):
            raise ValueError(f"Garment image not found: {self.garment_image}")
        
        self.start_time = datetime.now()
        try:
            self._job_id = self.client.create_job(
                model_image_path=self.model_image,
                garment_image_path=self.garment_image,
                clothes_type=self.params.get("category", "upper_body"),
                prompt=self.params.get("prompt", "")
            )
            self.status = "processing"
            return self._job_id
        except Exception as e:
            raise Exception(f"VModel job creation failed: {str(e)}")
    
    def check_status(self) -> Tuple[bool, Optional[Union[List[str], Exception]]]:
        """Check the status of the try-on process."""
        if not self._job_id:
            return True, Exception("No job ID available. Run the try-on first.")
        
        try:
            self.result_urls = self.client.fetch_job(
                self._job_id,
                max_attempts=self.params.get("max_attempts", 60),
                delay=self.params.get("delay", 5)
            )
            self.status = "completed"
            self.end_time = datetime.now()
            self.time_taken = self.end_time - self.start_time
            
            # Download if auto_download is enabled
            if self.auto_download and self.download_path and self.result_urls:
                self.client.download_image(self.result_urls[0], self.download_path)
            
            return True, self.result_urls
        except TimeoutError:
            return False, None
        except Exception as e:
            return True, Exception(f"VModel job check failed: {str(e)}")
    
    def get_result(self) -> Dict[str, Any]:
        """Get the try-on result."""
        if not self.result_urls:
            raise ValueError("No result available. Run the try-on first.")
            
        result = {
            "urls": self.result_urls,
            "source_images": {
                "model": self.model_image,
                "garment": self.garment_image
            },
            "category": self.params.get("category", "upper_body"),
            "prompt": self.params.get("prompt", ""),
            "timing": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "time_taken": str(self.time_taken) if self.time_taken else None
            }
        }
        
        if self.auto_download and self.download_path:
            result["local_path"] = self.download_path
            
        return result
```

### 3. Service Registration (services/vton/__init__.py)

Add this line to register the new service:

```python
# Add import
from .vmodel import VModelVTON

# Add registration
ServiceFactory.register(ServiceType.VTON, "vmodel", VModelVTON)
```

### 4. Configuration Update (utils/config.py)

Add this function to handle VModel API token:

```python
def get_vmodel_api_token() -> str:
    """Get VModel API token from environment variables."""
    return get_env_or_raise("VMODEL_API_KEY")
```

### 5. Example Script (examples/vmodel_example.py)

```python
"""Example script for using VModel virtual try-on service."""

import os
from pathlib import Path
from tryon_tray.factory import get_service
from tryon_tray.utils.config import load_config

def main():
    # Load configuration
    load_config()
    
    # Setup paths
    script_dir = Path(__file__).parent
    inputs_dir = script_dir / "inputs"
    outputs_dir = script_dir / "outputs"
    
    model_image = str(inputs_dir / "person.jpg")
    garment_image = str(inputs_dir / "garment.jpeg")
    output_path = str(outputs_dir / "result_vmodel.png")
    
    # Create outputs directory if it doesn't exist
    outputs_dir.mkdir(exist_ok=True)
    
    try:
        # Initialize service
        service = get_service(
            service_type="vton",
            model_name="vmodel",
            model_image=model_image,
            garment_image=garment_image,
            auto_download=True,
            download_path=output_path,
            params={
                "category": "upper_body",
                "prompt": "A stylish look",
                "max_attempts": 60,
                "delay": 5
            }
        )
        
        print("Initiating try-on process...")
        job_id = service.run()
        print(f"Job ID: {job_id}")
        
        print("Polling for results...")
        while True:
            is_complete, result = service.check_status()
            if is_complete:
                if isinstance(result, Exception):
                    raise result
                break
        
        result = service.get_result()
        print("\nProcess completed successfully!")
        print(f"Result saved to: {result.get('local_path')}")
        print(f"Result URLs: {result.get('urls')}")
        print(f"Time taken: {result.get('timing', {}).get('time_taken')}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
```

## Configuration

Add this to your `.env` file:
```
VMODEL_API_KEY=your_api_key_here
```

## Testing

1. Place test images in `examples/inputs/`:
   - `person.jpg` - Model image
   - `garment.jpeg` - Garment image

2. Run the example:
```bash
python examples/vmodel_example.py
```

## Best Practices

1. Follow existing patterns in the codebase
2. Use type hints
3. Handle errors gracefully
4. Add proper logging
5. Document public interfaces
6. Follow PEP 8 style guide 

## Running the Example

1. Install dependencies:
```bash
pip install requests python-dotenv
```

2. Set up environment and images:
   - Create `.env` file in `tryon_tray/examples/` with your API keys
   - Place model image as `person.jpg` in `examples/inputs/`
   - Place garment image as `garment.jpeg` in `examples/inputs/`

3. Run the example:
```bash
# From the project root directory
python tryon_tray/examples/vmodel_example.py
```

## Troubleshooting

Common issues and solutions:

1. **ModuleNotFoundError**: Make sure you've installed the package in development mode using `pip install -e tryon_tray/python`

2. **Missing API Key**: Ensure you've set up the `VMODEL_API_KEY` in your `.env` file

3. **Image Not Found**: Verify that test images are placed in the correct location (`examples/inputs/`)

## Testing During Development

1. Run unit tests:
```bash
# From tryon_tray/python directory
python -m pytest tests/
```

2. Test the service manually:
```python
from tryon_tray.services.factory import get_service, ServiceType
from tryon_tray.utils.config import load_config

# Load config
load_config()

# Create service instance
service = get_service(
    service_type=ServiceType.VTON,
    model_name="vmodel",
    model_image="path/to/model.jpg",
    garment_image="path/to/garment.jpg"
)

# Run try-on
job_id = service.run()
``` 