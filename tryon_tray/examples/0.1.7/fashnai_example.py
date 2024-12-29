import sys
import os
from pathlib import Path

# Add the python/src directory to Python path
repo_root = Path(__file__).parent.parent
sys.path.append(str(repo_root / "python" / "src"))

from dotenv import load_dotenv
from tryon_tray.api.vton import VTON
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Setup paths
script_dir = Path(__file__).parent
inputs_dir = script_dir / "inputs"
outputs_dir = script_dir / "outputs"

# Create directories if they don't exist
inputs_dir.mkdir(exist_ok=True)
outputs_dir.mkdir(exist_ok=True)

# Input paths
model_image = str(inputs_dir / "person.jpg")
garment_image = str(inputs_dir / "garment.jpeg")
output_path = str(outputs_dir / "result_fashnai.jpg")

print(f"Using model image: {model_image}")
print(f"Using garment image: {garment_image}")
print(f"Output will be saved to: {output_path}")

# Generate try-on
result = VTON(
    model_image=model_image,
    garment_image=garment_image,
    model_name="fashnai",
    auto_download=True,
    download_path=output_path,
    show_polling_progress=True,
    # Optional parameters
    category="tops",
    mode="quality"
)

# Print results
print("\nGeneration completed!")
if result.get('timing'):
    print(f"Time taken: {result['timing']['time_taken']}")

if result.get('local_path'):
    print(f"\nImage downloaded to: {result['local_path']}")

print(f"\nResult URLs: {result['urls']}")

