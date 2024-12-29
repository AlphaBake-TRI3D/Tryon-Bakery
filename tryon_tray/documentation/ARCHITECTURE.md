# Architecture Overview

This document describes the architecture of the Tryon-Bakery package.

## Directory Structure

```
tryon_tray/python/src/tryon_tray/
├── api/                    # High-level API interfaces
│   ├── video_gen.py       # Video generation API
│   └── vton.py           # Virtual try-on API
├── base/                  # Base classes
│   ├── service.py        # Base service class
│   ├── video.py         # Base video generation class
│   └── vton.py          # Base virtual try-on class
├── services/             # Service implementations
│   ├── video/           # Video generation services
│   │   ├── __init__.py
│   │   └── kling.py     # Kling AI video service
│   └── vton/            # Virtual try-on services
│       ├── __init__.py
│       ├── fashnai.py   # Fashn.ai service
│       ├── klingai.py   # Kling AI VTON service
│       └── replicate.py # Replicate VTON service
├── types/               # Type definitions
│   ├── video.py        # Video generation types
│   └── vton.py         # Virtual try-on types
└── utils/              # Utility functions
    ├── config.py       # Configuration handling
    └── file_io.py      # File I/O utilities
```

## Core Components

### Base Classes

1. `BaseService`: Abstract base class for all services
   - Handles common functionality like API key management
   - Defines interface for service operations

2. `BaseVideoGen`: Base class for video generation services
   - Extends `BaseService`
   - Handles video generation specifics
   - Manages polling and result downloads

3. `BaseVTON`: Base class for virtual try-on services
   - Extends `BaseService`
   - Handles try-on specifics
   - Manages polling and result downloads

### Service Types

1. Video Generation Services:
   - `KlingVideoGen`: Implements video generation using Kling AI
   - Supports different modes and durations
   - Handles video download and progress tracking

2. Virtual Try-on Services:
   - `FashnaiVTON`: Fashn.ai implementation
     - Supports quality and speed modes
     - Handles garment categories and parameters
     - Uses polling for async results
   - `KlingaiVTON`: Kling AI VTON implementation
     - Uses JWT authentication
     - Supports various garment types
     - Uses polling for async results
   - `ReplicateVTON`: Replicate implementation
     - Uses Replicate's IDM-VTON model
     - Supports additional parameters like steps and cropping
     - Direct result handling (no polling needed)

### Factory Pattern

The package uses a factory pattern to create service instances:
- `ServiceFactory`: Central factory for creating service instances
- Supports multiple service types (VTON, Video)
- Dynamic service registration
- Type-safe service creation

### High-level APIs

1. Video Generation API (`video_gen.py`):
   ```python
   result = generate_video(
       source_image="person.jpg",
       prompt="walking naturally",
       model_name="kling-v1-5",
       mode="std",
       duration="5"
   )
   ```

2. Virtual Try-on API (`vton.py`):
   ```python
   # For async services (Fashn.ai, Kling.ai)
   result = VTON(
       model_image="person.jpg",
       garment_image="garment.jpg",
       model_name="fashnai",
       category="tops",
       mode="quality",
       show_polling_progress=True
   )
   
   # For direct services (Replicate)
   result = VTON(
       model_image="person.jpg",
       garment_image="garment.jpg",
       model_name="replicate",
       category="upper_body",
       steps=30,
       seed=42
   )
   ```

### Type System

1. Video Types:
   - `VideoModelVersion`: Available model versions
   - `VideoMode`: Generation modes
   - `VideoDuration`: Supported durations
   - `VideoGenParams`: Generation parameters
   - `VideoGenResponse`: Generation results

2. VTON Types:
   - `VTONProvider`: Available providers
   - `VTONMode`: Try-on modes
   - `VTONCategory`: Garment categories
   - `VTONParams`: Try-on parameters
   - `VTONResponse`: Try-on results

### Utilities

1. Configuration (`config.py`):
   - Environment variable management:
     ```python
     # Get credentials with error handling
     access_id, api_key = get_klingai_credentials()
     api_key = get_fashnai_credentials()
     token = get_replicate_credentials()
     ```
   - Service-specific configuration functions
   - Centralized credential management

2. File I/O (`file_io.py`):
   - Image encoding/decoding:
     ```python
     # Basic base64 encoding
     b64_str = image_to_base64("image.jpg")
     
     # With data URI prefix and MIME type
     data_uri = base64_with_prefix("image.png")
     ```
   - File downloads with progress tracking:
     ```python
     # Download with chunk handling
     path = download_file(
         url="https://example.com/image.jpg",
         output_path="downloads/image.jpg",
         chunk_size=8192
     )
     ```
   - Supports multiple image formats (JPEG, PNG, GIF)
   - Error handling and logging

## Service Flow

1. Service Creation:
   ```python
   service = ServiceFactory.get_service(
       service_type=ServiceType.VTON,
       model_name="fashnai",
       **params
   )
   ```

2. Operation Flow (Async Services):
   ```
   1. Initialize Service
   2. Validate Parameters
   3. Prepare Payload
   4. Start Operation (run)
   5. Poll for Results (check_status)
   6. Download Results (if auto_download)
   7. Return Results (get_result)
   ```

3. Operation Flow (Direct Services):
   ```
   1. Initialize Service
   2. Validate Parameters
   3. Prepare Payload
   4. Run and Get Results (run)
   5. Download Results (if auto_download)
   6. Return Results (get_result)
   ```

## Error Handling

- Service-specific errors extend base exceptions
- Proper error propagation through layers
- Detailed error messages with service codes
- File I/O error handling with fallbacks

## Future Extensions

To add a new service:
1. Create new service class extending appropriate base
2. Implement required abstract methods
3. Register service in factory
4. Add service-specific types
5. Update documentation
6. Add credential management
7. Implement file handling if needed
