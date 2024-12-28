import os
import json
from aidc.base import IopClient, IopRequest
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

AIDC_APP_KEY = os.getenv("AIDC_ACCESS_ID")
AIDC_APP_SECRET = os.getenv("AIDC_API_KEY")

print("\nDebug: Credentials loaded:")
print(f"AIDC_ACCESS_ID: {AIDC_APP_KEY[:5]}..." if AIDC_APP_KEY else "AIDC_ACCESS_ID: Not set")
print(f"AIDC_API_KEY: {AIDC_APP_SECRET[:5]}..." if AIDC_APP_SECRET else "AIDC_API_KEY: Not set")

if not AIDC_APP_KEY or not AIDC_APP_SECRET:
    raise ValueError("Please set AIDC_ACCESS_ID and AIDC_API_KEY environment variables")

def run_tryon(garment_url, model_url=None):
    # Initialize the client
    client = IopClient("https://api.aidc-ai.com", AIDC_APP_KEY, AIDC_APP_SECRET)

    # Create a request object
    request = IopRequest("/ai/virtual/tryon")
    request.set_protocol('GOP')
    request.add_header("x-iop-trial", "true")

    # Prepare request parameters following the first example format
    params = [{
        "clothesList": [{
            "imageUrl": garment_url,
            "type": "tops"
        }],
        "viewType": "mixed",
        "generateCount": 4,
        "inputQualityDetect": 0
    }]

    if model_url:
        params[0]["modelImage"] = [model_url]
    else:
        params[0]["model"] = {
            "base": "General",
            "gender": "female",
            "style": "universal_1",
            "body": "slim"
        }

    # Add request parameters
    request.add_api_param("requestParams", json.dumps(params))

    # Execute the request
    response = client.execute(request)
    
    # Parse the response
    if isinstance(response.body, dict):
        if response.body.get("code") == "0":
            print("Request successful!")
            result = response.body["data"]["result"]
            task_id = result["taskId"]
            print("Task ID:", task_id)
            return task_id
        else:
            print("Request failed!")
            print("Error type:", response.body.get("type"))
            print("Error code:", response.body.get("code"))
            print("Error message:", response.body.get("message"))
            print("Request ID:", response.body.get("request_id"))
    else:
        print("Unexpected response format:", response.body)

def poll_results(task_id, max_attempts=60, delay=5):
    """Poll for the results of a try-on task
    
    Args:
        task_id: The task ID to poll for
        max_attempts: Maximum number of polling attempts
        delay: Delay between polling attempts in seconds
    
    Returns:
        list: List of image URLs if successful, None if failed
    """
    client = IopClient("https://api.aidc-ai.com", AIDC_APP_KEY, AIDC_APP_SECRET)
    
    for attempt in range(max_attempts):
        print(f"\nPolling attempt {attempt + 1}/{max_attempts}")
        
        # Create request for polling
        request = IopRequest("/ai/virtual/tryon-results")
        request.set_protocol('GOP')
        request.add_header("x-iop-trial", "true")
        request.add_api_param("task_id", task_id)
        
        # Execute request
        response = client.execute(request)
        
        if isinstance(response.body, dict):
            if response.body.get("code") == "0":
                data = response.body.get("data", {})
                task_status = data.get("taskStatus")
                print(f"Task status: {task_status}")
                
                if task_status == "finished":
                    # Extract image URLs from the response
                    task_results = data.get("taskResult", [])
                    image_urls = []
                    
                    for task_result in task_results:
                        result = task_result.get("taskResult", {}).get("result", {})
                        image_list = result.get("imageList", [])
                        for image in image_list:
                            image_urls.append({
                                "result_image": image.get("imageUrl"),
                                "garment_image": image.get("clothes")
                            })
                    
                    return image_urls
                elif task_status == "failed":
                    print("Task processing failed")
                    return None
                
                print(f"Task still processing. Waiting {delay} seconds...")
                time.sleep(delay)
            else:
                print("Poll request failed!")
                print("Error type:", response.body.get("type"))
                print("Error code:", response.body.get("code"))
                print("Error message:", response.body.get("message"))
                return None
        else:
            print("Unexpected response format:", response.body)
            return None
    
    print("Maximum polling attempts reached")
    return None

def save_results(image_urls, output_dir):
    """Save the result images to the output directory
    
    Args:
        image_urls: List of dictionaries containing result_image and garment_image URLs
        output_dir: Directory to save the images
    """
    if not image_urls:
        print("No images to save")
        return
        
    import requests
    from pathlib import Path
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    for i, image_data in enumerate(image_urls):
        result_url = image_data["result_image"]
        
        # Download and save the result image
        response = requests.get(result_url)
        if response.status_code == 200:
            output_path = output_dir / f"result_aidc_{i}.png"
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"Saved result image to {output_path}")
        else:
            print(f"Failed to download result image {i}")

def main():
    try:
        task_id = run_tryon(
            garment_url="https://speedtesttri3d.s3.ap-south-1.amazonaws.com/garment.jpeg",
            model_url="https://speedtesttri3d.s3.ap-south-1.amazonaws.com/person.jpg"
        )
        if task_id:
            print("Successfully submitted try-on request")
            print("Task ID for polling:", task_id)
            
            # Poll for results
            print("\nPolling for results...")
            image_urls = poll_results(task_id)
            
            if image_urls:
                print("\nTry-on completed successfully!")
                print(f"Generated {len(image_urls)} images")
                
                # Save the results
                print("\nSaving results...")
                save_results(image_urls, "outputs")
            else:
                print("\nFailed to get try-on results")
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    main()
