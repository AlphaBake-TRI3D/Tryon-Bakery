# Tryon Tray

A unified Python interface for AI-powered fashion technology services. Currently supports:
- Virtual try-on (VTON) via Fashn.ai, Replicate
- Video generation via Kling AI
- Quality check via Qwen (coming soon)
- Pose transfer (coming soon)

## Installation

```bash
pip install -e .
```

## Configuration

Create a `.env` file in your project root:
```bash
# Virtual Try-on APIs
FASHNAI_API_KEY=your_key_here
REPLICATE_API_KEY=your_key_here

# Video Generation APIs
KLINGAI_ACCESS_ID=your_id_here
KLINGAI_API_KEY=your_key_here
```

## Usage Examples

### Virtual Try-On
```python
from tryon_tray.api.vton import VTON

# Basic usage
result = VTON(
    model_image="person.jpg",
    garment_image="garment.jpg",
    model_name="fashnai"
)
print(result["urls"])

# With auto-download
result = VTON(
    model_image="person.jpg",
    garment_image="garment.jpg",
    model_name="replicate",
    auto_download=True,
    download_dir="outputs"
)
print(result["local_paths"])
```

### Video Generation
```python
from tryon_tray.api.video_gen import generate_video

# Basic usage
result = generate_video(
    source_image="person.jpg",
    prompt="person walking naturally",
    model_name="kling-v1-5",  # or "kling-v1"
    mode="std",               # or "pro"
    duration="5"             # or "10"
)
print(f"Video URL: {result.video_url}")

# Advanced options
result = generate_video(
    source_image="person.jpg",
    prompt="person walking naturally",
    model_name="kling-v1-5",
    mode="pro",
    duration="10",
    negative_prompt="bad quality, blurry",
    cfg_scale=0.7,
    seed=42
)
print(f"Video URL: {result.video_url}")
print(f"Task ID: {result.task_id}")
print(f"Created at: {result.created_at}")
```

### Quality Check (Coming Soon)
```python
from tryon_tray.api.quality import check_quality

result = check_quality(
    image="garment.jpg",
    model_name="qwen",
    checks=["blur", "lighting", "composition"]
)
print(result["scores"])
```

## Model Capabilities

### Virtual Try-on Models
- `fashnai`: Fashn.ai's VTON service
- `replicate`: Replicate's IDM-VTON model

### Video Generation Models
- `kling-v1`: Kling AI's V1 model
  - Supports standard and professional modes
  - 5 or 10 second videos
  - Configurable CFG scale and seed
- `kling-v1-5`: Kling AI's V1.5 model (latest)
  - Enhanced quality and stability
  - Same features as V1

## Error Handling

```python
try:
    result = generate_video(...)
except VideoGenError as e:
    print(f"API Error (Code {e.service_code}): {e.message}")
except ValueError as e:
    print(f"Invalid parameters: {e}")
except TimeoutError:
    print("Generation timed out")
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License
