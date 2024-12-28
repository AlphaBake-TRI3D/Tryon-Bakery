import os
import time
import json
from pathlib import Path
import dotenv
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from aidc.base import IopClient, IopRequest

dotenv.load_dotenv()

AIDC_APP_KEY = os.getenv("AIDC_ACCESS_ID")
AIDC_APP_SECRET = os.getenv("AIDC_API_KEY")

if not AIDC_APP_KEY or not AIDC_APP_SECRET:
    raise ValueError("Please set AIDC_ACCESS_ID and AIDC_API_KEY environment variables")

# Make sure we have the full URL with protocol
BASE_URL = "https://47.246.173.5"  # Using IP directly since DNS resolution is failing

def run_tryon(
    garment_url: str,
    model_url: str = None,
    garment_type: str = "tops",
    view_type: str = "mixed",
    generate_count: int = 4,
    input_quality_detect: int = 0,
):
    """Initialize the try-on process with AIDC API
    
    Args:
        garment_url: URL of the garment image
        model_url: Optional URL of the model image. If not provided, uses default models
        garment_type: Type of garment ("tops", "bottoms", "dresses")
        view_type: View type ("fullbody", "halfbody", "mixed")
        generate_count: Number of images to generate (1-8)
        input_quality_detect: Whether to filter low quality images (0 or 1)
    
    Returns:
        str: Task ID for polling results
    """
    # Validate garment type
    VALID_GARMENT_TYPES = {"tops", "bottoms", "dresses"}
    if garment_type not in VALID_GARMENT_TYPES:
        raise ValueError(f"Invalid garment type. Must be one of: {', '.join(VALID_GARMENT_TYPES)}")
    
    # Validate view type
    VALID_VIEW_TYPES = {"fullbody", "halfbody", "mixed"}
    if view_type not in VALID_VIEW_TYPES:
        raise ValueError(f"Invalid view type. Must be one of: {', '.join(VALID_VIEW_TYPES)}")
    
    # Validate generate count
    if not 1 <= generate_count <= 8:
        raise ValueError("generate_count must be between 1 and 8")

    # Initialize client
    print(f"\nInitializing client with:")
    print(f"BASE_URL: {BASE_URL}")
    print(f"APP_KEY: {AIDC_APP_KEY[:5]}...")  # Only print first few chars for security
    print(f"APP_SECRET: {AIDC_APP_SECRET[:5]}...")
    
    try:
        client = IopClient(BASE_URL, AIDC_APP_KEY, AIDC_APP_SECRET)
        print("Client initialized successfully")
    except Exception as e:
        print(f"Error initializing client: {str(e)}")
        raise

    try:
        request = IopRequest("/ai/virtual/tryon")
        print("Request object created successfully")
    except Exception as e:
        print(f"Error creating request: {str(e)}")
        raise
    
    # Add headers
    try:
        request.add_header("x-iop-trial", "true")
        request.add_header("Content-Type", "application/json")
        request.add_header("Host", "api.aidc-ai.com")  # Add Host header
        request.set_protocol('GOP')
        print("Headers and protocol set successfully")
    except Exception as e:
        print(f"Error setting headers: {str(e)}")
        raise
    
    # Prepare request parameters
    request_params = {
        "clothesList": [{
            "imageUrl": garment_url,
            "type": garment_type
        }],
        "viewType": view_type,
        "inputQualityDetect": input_quality_detect,
        "generateCount": generate_count
    }

    # Add model image if provided, otherwise use default model settings
    if model_url:
        request_params["modelImage"] = [model_url]
    else:
        request_params["model"] = {
            "base": "General",
            "gender": "female",
            "style": "universal_1",
            "body": "slim"
        }

    # Add request parameters as a single JSON string
    request_json = json.dumps([{"requestParams": request_params}])
    print("\nRequest parameters:")
    print(json.dumps(request_params, indent=2))
    print("\nFull request JSON:")
    print(request_json)
    
    request.add_api_param("requestParams", request_json)
    
    # Execute request
    print("\nPreparing to execute request...")
    print(f"Request URL: {BASE_URL}/ai/virtual/tryon")
    print("Request headers:", request._headers if hasattr(request, '_headers') else "No headers found")
    print("Request protocol:", request._protocol if hasattr(request, '_protocol') else "No protocol found")
    print("Request parameters:", request._api_params if hasattr(request, '_api_params') else "No parameters found")
    
    try:
        print("\nExecuting request...")
        print("Client object:", client)
        print("Client attributes:", dir(client))
        response = client.execute(request)
        print("Request executed successfully")
        
        print("\nResponse details:")
        print("Response object:", response)
        print("Response type:", type(response))
        print("Response attributes:", dir(response))
        
        if hasattr(response, 'getBody'):
            body = response.getBody()
            print("\nResponse body:", body)
            print("Body type:", type(body))
            
            try:
                response_data = json.loads(body)
                print("\nParsed response data:")
                print(json.dumps(response_data, indent=2))
            except json.JSONDecodeError as e:
                print(f"\nFailed to parse response body: {e}")
                print("Raw body:", body)
                raise
        else:
            print("\nNo getBody method found on response")
            if isinstance(response, (str, bytes)):
                print("Response content:", response)
                response_data = json.loads(response if isinstance(response, str) else response.decode())
            else:
                raise Exception("Unexpected response type")
            
    except Exception as e:
        print(f"\nError during request execution: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Error details: {repr(e)}")
        raise
    
    if response_data.get("resCode") != "200":
        raise Exception(f"API request failed: {response_data.get('resMessage')}")
    
    try:
        result = json.loads(response_data["data"]["result"])
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Failed to parse result: {e}")
        print("Response data:", response_data)
        raise Exception("Invalid result format from API")
        
    return result["taskId"]

def poll_status(task_id: str, max_attempts: int = 60, delay: int = 5):
    """Poll the status endpoint until completion or failure"""
    client = IopClient(BASE_URL, AIDC_APP_KEY, AIDC_APP_SECRET)
    
    for attempt in range(max_attempts):
        print(f"\nPolling attempt {attempt + 1}/{max_attempts}")
        request = IopRequest("/ai/virtual/tryon/result")
        request.add_api_param("taskId", task_id)
        
        print("Sending status check request...")
        response = client.execute(request)
        print("Got response, parsing...")
        
        try:
            body = response.getBody()
            print("Response body:", body)
            result = json.loads(body)
            print("Parsed result:", json.dumps(result, indent=2))
        except json.JSONDecodeError as e:
            print(f"Failed to parse response: {e}")
            print("Response content:", body)
            raise Exception("Invalid response from status check")
        
        if result.get("resCode") != "200":
            raise Exception(f"Status check failed: {result.get('resMessage')}")
            
        data = result.get("data", {})
        task_status = data.get("taskStatus")
        print(f"Task status: {task_status}")
        
        if task_status == "finished":
            return data.get("resultList", [])
        elif task_status == "failed":
            raise Exception("Task processing failed")
        
        print(f"Status: {task_status}. Waiting {delay} seconds...")
        time.sleep(delay)
    
    raise TimeoutError("Maximum polling attempts reached")

def save_results(results, output_dir: Path):
    """Save the generated images to the output directory"""
    output_dir.mkdir(exist_ok=True)
    
    for i, result in enumerate(results):
        if not result.get("resultList"):
            continue
            
        for j, image_data in enumerate(result["resultList"]):
            image_url = image_data.get("resultImage")
            if not image_url:
                continue
                
            output_path = output_dir / f"result_{i}_{j}.png"
            # Note: You'll need to implement the actual image download logic here
            print(f"Would save image from {image_url} to {output_path}")

def main():
    try:
        # Start the try-on process
        print("Initiating try-on process...")
        task_id = run_tryon(
            garment_url="https://speedtesttri3d.s3.ap-south-1.amazonaws.com/garment.jpeg",
            model_url="https://speedtesttri3d.s3.ap-south-1.amazonaws.com/person.jpg",
            garment_type="tops",
            view_type="mixed",
            generate_count=4
        )
        print(f"Task ID: {task_id}")
        
        # Poll for results
        print("Polling for results...")
        results = poll_status(task_id)
        
        # Save results
        print("Saving results...")
        save_results(results, Path(__file__).parent / "outputs")
        
        print("Process completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
