"""Example script for using VModel virtual try-on service."""

import os
from pathlib import Path
from tryon_tray.services.factory import get_service, ServiceType
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    # Setup paths
    script_dir = Path(__file__).parent
    inputs_dir = script_dir / "inputs"
    outputs_dir = script_dir / "outputs"
    
    
    # Load configuration from the examples directory
    
    
    model_image = str(inputs_dir / "person.jpg")
    garment_image = str(inputs_dir / "garment.jpeg")
    output_path = str(outputs_dir / "result_vmodel.png")
    
    # Create outputs directory if it doesn't exist
    outputs_dir.mkdir(exist_ok=True)
    
    try:
        # Initialize service
        service = get_service(
            service_type=ServiceType.VTON,
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