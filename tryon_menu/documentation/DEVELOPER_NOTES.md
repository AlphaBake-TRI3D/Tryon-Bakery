# Developer Notes for Tryon-Bakery Project

## Overview
The Tryon-Bakery project is a Django web application designed to benchmark and compare virtual try-on solutions. It supports both image and video models, providing a comprehensive platform for evaluating different try-on technologies.

## Project Structure
- **Backend Framework**: Django
- **Main Project**: `tryon_menu`
- **Storage**: AWS S3 for image and video storage

## Core Functionalities
1. **Virtual Try-On Model Integration**: Supports both image and video models.
2. **Benchmarking Capabilities**: Evaluates image-based try-on and video generation quality.
3. **Comparative Analysis Tools**: Provides tools for comparing different models.
4. **Results Visualization**: Displays results through a user-friendly web interface.

## Key Components
- **InputSet**: Stores pairs of garment and model images or videos. Includes fields for mode (image/video) and prompt (for video).
- **Tryon**: Stores result images or videos from different models. Includes mode and other metadata.
- **TryonBatch**: Groups multiple Tryon instances for batch processing.
- **RankedPair**: Manages user rankings of try-on results, using an Elo rating system.

## User Interface
- **Navbar Actions**: Includes options to create input sets and tryon batches for both images and videos.
- **Listing Pages**: Four main listing pages accessible from the navbar:
  - Leaderboard
  - InputSet List
  - TryonBatch List
  - Rankings

## Video Model Integration
- **Video Generation**: Supports video generation from static images with customizable parameters.
- **Video Storage**: Videos are stored in AWS S3, with metadata tracking and local download capabilities.
- **Video UI**: Includes video generation request forms, progress tracking, and video previews.

## Future Considerations
- Additional model integrations
- Enhanced comparison metrics
- Performance optimizations
- API accessibility

## Authentication System
- **User Management**: Standard Django authentication with custom views.
- **Templates**: Located in `main/templates/main/auth/`.
- **Security**: Includes CSRF protection, secure password storage, and session security.

## Elo Rating System
- Provides a dynamic method for ranking virtual try-on models based on performance.
- Integrated with the benchmarking and comparative analysis tools.

## Development Notes
- Ensure AWS credentials are securely managed and not included in version control.
- Use console email backend during development for testing email functionalities.
- Maintain style consistency through CSS variables and responsive design patterns.

## Recent Updates

### Video Mode Integration
- Added support for video models alongside image models.
- Updated `InputSet` and `Tryon` models to include a `mode` field to distinguish between image and video modes.
- Added a `prompt` field to the `InputSet` model for video-specific prompts.

### Template Updates
- Updated `tryonbatch_create_step1.html` to include a mode selection dropdown.
- Modified `tryonbatch_create_step2.html` to handle mode-specific logic for manual uploads, allowing video uploads when the mode is set to video.
- Adjusted `tryonbatch_detail.html` to display videos instead of images for video tryons, with autoplay and loop functionality.
- Added tabs to `tryonbatch_list.html` to filter and display tryon batches based on their mode (image or video).

### URL and View Adjustments
- Ensured URL patterns in `urls.py` can handle both image and video modes using query parameters.
- Updated views in `views.py` to process the new `mode` and `prompt` fields, storing mode information in session data for batch creation steps.

### Developer Notes
- The project now supports both image and video tryon models, providing flexibility in benchmarking and comparison.
- Ensure that the mode is correctly set in forms and processed in views to maintain consistency across the application.
- The UI has been enhanced to accommodate video content, ensuring a seamless user experience.

This documentation provides a high-level overview of the Tryon-Bakery project, its structure, and core functionalities. It serves as a guide for developers to understand the organization and purpose of the various components within the project. Further details can be found in the `InitialPRD.txt` and other documentation files within the project. 



------ Original Notes from Nitish ------
Start adding the developer notes in @documentation folder , new file DEVLOPER_NOTES.md

Right now in navbar create there are two actions , create inputset and create tryonbatch

Let's add two more buttons create inputset video , create tryonbatch video

Rename the existing into image 

Also, let's add mode - image or video into inputSet class as well 

we will keep the garment image null and will let them upload only one image 

let's also add prompt field in the inputSet , this we will let the user edit for video 

but for image - we will just let them those two input images 

in tryonbatch video , the step1.html will be the same , only that we will be filtering the video models vs image models 

Handle this from the url , lets use the same view 

in step2.html , we will let them upload image if it's a manual upload 

similarly in tryonbatch detail , if it's image the same will be displayed , but for video 

we will show only person image and prompt and skip the garment image and we will show videos instead of images in the same frame , let's auto play all the available videos in loop 

the files we need to edit could be @views.py @utils.py @urls.py 
@tryonbatch_create_step1.html 
@tryonbatch_create_step2.html @tryonbatch_detail.html 


in @tryonbatch_list.html , let there be two tabs , image and video will show accrodingly 

we will have to make changes to @models.py , modifying class InputSet 

add mode in Tryon as well and other changes if any

first add developer documentation , now that I outlined how to add video models as well , and there are 4 listing pages from navabar 

leaderboard , inputsetlist, tryonbatchlist, rankings 

also look at @InitialPRD.txt , which has some unnecessary information also , like number of lines and some random stuff 

with this core context , write a good developer oriented documentation of how the files are organised and functionalities , multiple category of models etc 

Then will start implemeting the video mode step by step