# Tryon-Tray

A Python package for virtual try-on services integration, supporting multiple VTON (Virtual Try-On)providers.


## Installation

```sh
pip install tryon-tray
```

## Usage

```python
# Load environment variables


from dotenv import load_dotenv
from tryon_tray.vton_api import VTON
from datetime import datetime
load_dotenv()
model_image = "inputs/person.jpg"
garment_image = "inputs/garment.jpeg"

#model_list = ["fashnai", "klingai","replicate"] 
result = VTON(
    model_image=model_image,
    garment_image=garment_image,
    model_name="fashnai", 
    auto_download=True,
    download_path="result.jpg",
    show_polling_progress=True,
    # Optional parameters
    category="tops",
    mode="quality",
)

print("Time taken: ",result['timing']['time_taken'])

```

## Features

- Multiple VTON service providers support  
- Automatic image downloading   
- Progress tracking 

## Configuration

Create a .env file with your API keys:

```sh
FASHNAI_API_KEY=your_fashnai_key
KLINGAI_API_KEY=your_klingai_key
REPLICATE_API_TOKEN=your_replicate_token
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
- `model_name`: Service provider ("fashnai", "klingai", "replicate") 
- `auto_download`: Automatically download generated images  
- `download_dir`: Directory for downloaded images  
- `polling_interval`: Time between status checks (seconds)`
- `show_polling_progress`: Show progressbar during generation   
- `category`: Garment category ("tops", "dresses", etc.)  
- `mode`: Generation mode ("quality" or "speed")  
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
