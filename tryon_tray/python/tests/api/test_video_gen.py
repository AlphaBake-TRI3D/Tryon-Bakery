import pytest
from unittest.mock import patch, MagicMock
from tryon_tray.api.video_gen import generate_video
from tryon_tray.types.video import VideoGenResponse, VideoModelVersion, VideoMode, VideoDuration
from tryon_tray.services.factory import ServiceType

@pytest.fixture
def mock_env():
    with patch.dict('os.environ', {
        'KLINGAI_ACCESS_ID': 'test_id',
        'KLINGAI_API_KEY': 'test_key'
    }):
        yield

@pytest.fixture
def mock_image(tmp_path):
    """Create a temporary test image."""
    image_path = tmp_path / "test.jpg"
    image_path.write_bytes(b"fake image data")
    return str(image_path)

def test_generate_video_integration(mock_env, mock_image):
    """Test the full video generation flow with mocked API calls."""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        
        # Mock API responses
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {
            "data": {"task_id": "test_task_123"}
        }
        
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            "data": {
                "task_status": "succeed",
                "task_id": "test_task_123",
                "created_at": 1234567890,
                "updated_at": 1234567891,
                "task_result": {
                    "videos": [{
                        "url": "https://example.com/video.mp4",
                        "duration": "5"
                    }]
                }
            }
        }
        
        # Test with all parameters
        result = generate_video(
            source_image=mock_image,
            prompt="person walking naturally",
            model_name=VideoModelVersion.KLING_V1_5.value,
            mode=VideoMode.STANDARD.value,
            duration=VideoDuration.FIVE.value,
            negative_prompt="bad quality",
            cfg_scale=0.7,
            seed=42
        )
        
        # Verify result
        assert isinstance(result, VideoGenResponse)
        assert result.video_url == "https://example.com/video.mp4"
        assert result.task_id == "test_task_123"
        assert result.created_at == 1234567890
        assert result.updated_at == 1234567891
        
        # Verify API calls
        assert mock_post.called
        assert mock_get.called
        
        # Verify request payload
        post_call = mock_post.call_args
        assert "image" in post_call.kwargs["json"]
        assert post_call.kwargs["json"]["prompt"] == "person walking naturally"
        assert post_call.kwargs["json"]["mode"] == "std"

def test_generate_video_error_handling(mock_env, mock_image):
    """Test error handling in the video generation flow."""
    with patch('requests.post') as mock_post:
        # Mock API error
        mock_post.return_value.ok = False
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "code": "1201",
            "message": "Invalid parameters"
        }
        
        with pytest.raises(Exception) as exc:
            generate_video(
                source_image=mock_image,
                prompt="test prompt"
            )
        
        assert "Invalid parameters" in str(exc.value)

def test_generate_video_timeout(mock_env, mock_image):
    """Test handling of timeout during video generation."""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        
        # Mock initial success
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {
            "data": {"task_id": "test_task_123"}
        }
        
        # Mock perpetual "processing" status
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            "data": {
                "task_status": "processing"
            }
        }
        
        with pytest.raises(TimeoutError):
            generate_video(
                source_image=mock_image,
                prompt="test prompt"
            ) 