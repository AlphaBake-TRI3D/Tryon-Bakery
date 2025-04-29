# Tryon-Tray

A Python package for virtual try-on services integration, supporting multiple VTON (Virtual Try-On)providers.


## Installation

```sh
pip install tryon-tray
```

## Usage
```python
# Using Alphabake's virtual try-on API

from dotenv import load_dotenv
from tryon_tray.vton_api import VTON
load_dotenv()

result = VTON(
    model_image="inputs/person.jpg",
    garment_image="inputs/garment.jpeg",
    model_name="alphabake",
    auto_download=True,
    download_path="result_alphabake.png",
    show_polling_progress=True,
    # Alphabake specific parameters
    mode="balanced",  # Options: 'fast', 'balanced', or 'quality'
    garment_name="garment-example",
    tryon_name="tryon-example"
)

print(f"Result saved to: {result.get('local_paths')}")
print(f"Time taken: {result['timing']['time_taken']}")
```

### Exploring Available Models

```python
# Discover available models and their parameters
from tryon_tray import get_available_models, get_model_params, get_model_sample_config

# List all available models
all_models = get_available_models()
print("Available models:", all_models)

# List just the virtual try-on models
vton_models = get_available_models(category="vton")
print("VTON models:", vton_models)

# List video models
video_models = get_available_models(category="video")
print("Video models:", video_models)

# Get parameters for a specific model
alphabake_params = get_model_params("alphabake")
print("Alphabake parameters:", alphabake_params)

# Get a sample configuration for a model
sample_config = get_model_sample_config("klingai")
print("Sample KlingAI config:", sample_config)

# Use the sample config directly
from dotenv import load_dotenv
from tryon_tray import VTON
load_dotenv()

config = get_model_sample_config("fashnai")
result = VTON(model_name="fashnai", **config)
```

## Features

- Multiple VTON service providers support  
- Automatic image downloading   
- Progress tracking 
- Model discovery and parameter exploration

## Configuration

Create a .env file with your API keys:

```sh
FASHNAI_API_KEY=your_fashnai_key
KLINGAI_API_KEY=your_klingai_key
REPLICATE_API_TOKEN=your_replicate_token
ALPHABAKE_API_KEY=your_alphabake_key
```

## Sample Response


```python
{
  "urls": ["https:/..."],  // Generated image URLs
  "local_paths": ["path/to/downloaded/image.jpg"],  // Downloaded file paths
  "timing": {
    "time_taken": datetime.timedelta  // Total processing time
  }
}
```

## Parameters

- `model_image`: Path to the person/model image  
- `garment_image`: Path to the garment image  
- `model_name`: Service provider ("fashnai", "klingai", "replicate", "alphabake") 
- `auto_download`: Automatically download generated images  
- `download_dir`: Directory for downloaded images  
- `polling_interval`: Time between status checks (seconds)`
- `show_polling_progress`: Show progressbar during generation   
- `category`: Garment category ("tops", "dresses", etc.)  
- `mode`: Generation mode ("quality" or "speed" for most APIs, "fast"/"balanced"/"quality" for alphabake)  
- `adjust_hands`: Adjust hand positions in output  
- `restore_background`: Preserve original image background 


## Response Format

- **URLs**! for generated images  
- **Local paths**! to downloaded images  
- **Timing!* information (time taken for processing)



## License

MIT License

## Contributing

Contributions are wellcome! Please feel free to submit a Pull Request.
