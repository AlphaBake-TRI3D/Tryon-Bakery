from pathlib import Path
from dotenv import load_dotenv
from tryon_tray.vton_api import VTON
from datetime import datetime

def main():
    # Load environment variables from the same directory as this script
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    # Setup paths
    script_dir = Path(__file__).parent
    input_dir = script_dir / "inputs"
    output_dir = script_dir / "outputs"
    
    # Input images
    model_image = str(input_dir / "person.jpg")
    garment_image = str(input_dir / "garment.jpeg")
    
    try:
        print("Starting virtual try-on with Fashn.ai...")
        result = VTON(
            model_image=model_image,
            garment_image=garment_image,
            model_name="fashnai",
            auto_download=True,
            download_dir=str(output_dir),
            # Polling configuration
            polling_interval=1,
            show_polling_progress=True,
            # Optional parameters
            category="tops",
            mode="quality",
            adjust_hands=True,
            restore_background=True
        )
        
        print("\nGenerated image URLs:")
        for url in result["urls"]:
            print(f"- {url}")
            
        print("\nDownloaded images:")
        for path in result["local_paths"]:
            print(f"- {path}")
            
        # Print timing information
        print(f"Total Time Taken: {result['timing']['time_taken'].total_seconds():.2f} seconds")
            
        print("\nProcess completed successfully!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main() 