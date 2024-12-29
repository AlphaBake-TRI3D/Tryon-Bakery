import sys
import os
from pathlib import Path

# Add the python/src directory to Python path
repo_root = Path(__file__).parent.parent
sys.path.append(str(repo_root / "python" / "src"))

from dotenv import load_dotenv
from tryon_tray.api.vton import VTON
from datetime import datetime
import time

# Load environment variables from .env file
load_dotenv()

# Example URLs (replace with your own hosted images)
model_url = "https://replicate.delivery/pbxt/KgwTlhCMvDagRrcVzZJbuozNJ8esPqiNAIJS3eMgHrYuHmW4/KakaoTalk_Photo_2024-04-04-21-44-45.png"
garment_url = "https://replicate.delivery/pbxt/KgwTlZyFx5aUU3gc5gMiKuD5nNPTgliMlLUWx160G4z99YjO/sweater.webp"

# Setup output path
script_dir = Path(__file__).parent
outputs_dir = script_dir / "outputs"
outputs_dir.mkdir(exist_ok=True)
output_path = str(outputs_dir / f"result_replicate_{int(time.time())}.jpg")

print(f"Using model image URL: {model_url}")
print(f"Using garment image URL: {garment_url}")
print(f"Output will be saved to: {output_path}")

# Generate try-on
result = VTON(
    model_image=model_url,
    garment_image=garment_url,
    model_name="replicate",
    auto_download=True,
    download_path=output_path,
    show_polling_progress=True,
    # Optional parameters specific to Replicate
    category="upper_body",
    steps=30,
    seed=42,
    crop=False,
    force_dc=False,
    mask_only=False,
    garment_des="cute pink top"  # Optional garment description
)

# Print results
print("\nGeneration completed!")
if result.get('timing'):
    print(f"Time taken: {result['timing']['time_taken']}")

if result.get('local_path'):
    print(f"\nImage downloaded to: {result['local_path']}")

print(f"\nResult URLs: {result['urls']}") 