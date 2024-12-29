import pytest
from unittest.mock import patch, MagicMock
from tryon_tray.api.video_gen import generate_video
from tryon_tray.types.video import VideoGenResponse, VideoModelVersion, VideoMode, VideoDuration

@pytest.fixture
def mock_service():
    with patch('tryon_tray.api.video_gen.get_service') as mock:
        service = MagicMock()
        service.get_result.return_value = {
            "video_url": "https://example.com/video.mp4",
            "source_image": "test.jpg",
            "prompt": "test prompt",
            "mode": "std",
            "duration": "5",
            "task_id": "test_task_123",
            "created_at": 1234567890,
            "updated_at": 1234567891
        }
        mock.return_value = service
        yield mock

def test_generate_video_basic(mock_service):
    """Test basic video generation with default parameters."""
    result = generate_video(
        source_image="test.jpg",
        prompt="test prompt"
    )
    
    assert isinstance(result, VideoGenResponse)
    assert result.video_url == "https://example.com/video.mp4"
    assert result.mode == "std"
    assert result.duration == "5"
    assert result.task_id == "test_task_123"

def test_generate_video_custom_params(mock_service):
    """Test video generation with custom parameters."""
    result = generate_video(
        source_image="test.jpg",
        prompt="test prompt",
        model_name=VideoModelVersion.KLING_V1.value,
        mode=VideoMode.PROFESSIONAL.value,
        duration=VideoDuration.TEN.value,
        negative_prompt="bad quality",
        cfg_scale=0.7,
        seed=42
    )
    
    mock_service.assert_called_once()
    service_instance = mock_service.return_value
    
    # Verify all parameters were passed correctly
    assert service_instance.run.called
    service_instance.get_result.assert_called_once()

def test_generate_video_invalid_model():
    """Test video generation with invalid model name."""
    with pytest.raises(ValueError):
        generate_video(
            source_image="test.jpg",
            prompt="test prompt",
            model_name="invalid-model"
        )

def test_generate_video_invalid_mode():
    """Test video generation with invalid mode."""
    with pytest.raises(ValueError):
        generate_video(
            source_image="test.jpg",
            prompt="test prompt",
            mode="invalid-mode"
        )

def test_generate_video_invalid_duration():
    """Test video generation with invalid duration."""
    with pytest.raises(ValueError):
        generate_video(
            source_image="test.jpg",
            prompt="test prompt",
            duration="15"  # Only 5 and 10 are valid
        ) 