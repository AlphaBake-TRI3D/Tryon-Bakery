import os
import replicate
import dotenv
from pathlib import Path
import requests
import json

dotenv.load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise ValueError("Please set REPLICATE_API_TOKEN environment variable")

def run_idm_vton(output_path: str):
    """Run the IDM-VTON model on Replicate with detailed parameters"""
    output = replicate.run(
        "cuuupid/idm-vton:c871bb9b046607b680449ecbae55fd8c6d945e0a1948644bf2361b3d021d3ff4",
        input={
            "crop": False,
            "seed": 42,
            "steps": 30,
            "category": "upper_body",
            "force_dc": False,
            "garm_img": "https://replicate.delivery/pbxt/KgwTlZyFx5aUU3gc5gMiKuD5nNPTgliMlLUWx160G4z99YjO/sweater.webp",
            "human_img": "https://replicate.delivery/pbxt/KgwTlhCMvDagRrcVzZJbuozNJ8esPqiNAIJS3eMgHrYuHmW4/KakaoTalk_Photo_2024-04-04-21-44-45.png",
            "mask_only": False,
            "garment_des": "cute pink top"
        }
    )
    
    # Check if the output is a FileOutput object
    if isinstance(output, replicate.helpers.FileOutput):
        # Read the content of the file and save it
        with open(output_path, 'wb') as f:
            f.write(output.read())
        return output_path  # Return the local file path for consistency
    
    raise ValueError("The output is not a valid FileOutput object.")

def download_image(file_path: str, output_path: str):
    """Move the generated image to the desired location"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.rename(file_path, output_path)
    print(f"Image successfully moved to {output_path}")

def main():
    # Setup paths
    script_dir = Path(__file__).parent
    outputs_dir = script_dir / "outputs"
    
    # Create outputs directory if it doesn't exist
    outputs_dir.mkdir(exist_ok=True)
    
    try:
        # Start the try-on process
        print("Initiating try-on process...")
        output_path = outputs_dir / "result_replicate_idm_vton.png"
        output_urls = run_idm_vton(output_path)
        
            
        print("Process completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 