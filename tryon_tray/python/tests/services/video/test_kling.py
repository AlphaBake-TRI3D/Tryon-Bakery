import pytest
from unittest.mock import patch, MagicMock
import jwt
import time
from tryon_tray.services.video.kling import KlingVideoGen
from tryon_tray.types.video import VideoGenError

@pytest.fixture
def mock_env():
    with patch.dict('os.environ', {
        'KLINGAI_ACCESS_ID': 'test_id',
        'KLINGAI_API_KEY': 'test_key'
    }):
        yield

@pytest.fixture
def mock_requests():
    with patch('tryon_tray.services.video.kling.requests') as mock:
        yield mock

@pytest.fixture
def service(mock_env):
    return KlingVideoGen(
        source_image="test.jpg",
        prompt="test prompt",
        mode="std",
        duration="5"
    )

def test_init(mock_env):
    """Test service initialization."""
    service = KlingVideoGen(
        source_image="test.jpg",
        prompt="test prompt"
    )
    assert service.access_id == "test_id"
    assert service.api_key == "test_key"
    assert service.task_id is None
    assert service.created_at is None
    assert service.updated_at is None

def test_validate_parameters_valid(service):
    """Test parameter validation with valid inputs."""
    service.validate_parameters()  # Should not raise

def test_validate_parameters_invalid_model():
    """Test parameter validation with invalid model."""
    with pytest.raises(ValueError, match="Invalid model version"):
        KlingVideoGen(
            source_image="test.jpg",
            prompt="test",
            model_name="invalid-model"
        ).validate_parameters()

def test_validate_parameters_invalid_mode():
    """Test parameter validation with invalid mode."""
    with pytest.raises(ValueError, match="Invalid mode"):
        KlingVideoGen(
            source_image="test.jpg",
            prompt="test",
            mode="invalid-mode"
        ).validate_parameters()

def test_validate_parameters_invalid_duration():
    """Test parameter validation with invalid duration."""
    with pytest.raises(ValueError, match="Invalid duration"):
        KlingVideoGen(
            source_image="test.jpg",
            prompt="test",
            duration="15"
        ).validate_parameters()

def test_encode_jwt_token(service):
    """Test JWT token generation."""
    token = service._encode_jwt_token()
    decoded = jwt.decode(token, "test_key", algorithms=["HS256"])
    
    assert decoded["iss"] == "test_id"
    assert decoded["exp"] > int(time.time())
    assert decoded["nbf"] < int(time.time())

def test_prepare_payload(service):
    """Test API payload preparation."""
    with patch('tryon_tray.services.video.kling.KlingVideoGen._image_to_base64') as mock_b64:
        mock_b64.return_value = "base64_image_data"
        payload = service.prepare_payload()
        
        assert payload["image"] == "base64_image_data"
        assert payload["prompt"] == "test prompt"
        assert payload["mode"] == "std"
        assert payload["duration"] == "5"
        assert payload["cfg_scale"] == 0.5

def test_run_success(service, mock_requests):
    """Test successful video generation."""
    # Mock create task response
    create_response = MagicMock()
    create_response.ok = True
    create_response.json.return_value = {
        "data": {"task_id": "test_task_123"}
    }
    
    # Mock poll response
    poll_response = MagicMock()
    poll_response.ok = True
    poll_response.json.return_value = {
        "data": {
            "task_status": "succeed",
            "task_id": "test_task_123",
            "task_result": {
                "videos": [{
                    "url": "https://example.com/video.mp4"
                }]
            }
        }
    }
    
    mock_requests.post.return_value = create_response
    mock_requests.get.return_value = poll_response
    
    service.run()
    
    assert service.task_id == "test_task_123"
    assert service.result_url == "https://example.com/video.mp4"

def test_run_api_error(service, mock_requests):
    """Test handling of API errors."""
    error_response = MagicMock()
    error_response.ok = False
    error_response.status_code = 400
    error_response.json.return_value = {
        "code": "1201",
        "message": "Invalid parameters"
    }
    
    mock_requests.post.return_value = error_response
    
    with pytest.raises(VideoGenError) as exc:
        service.run()
    
    assert exc.value.status_code == 400
    assert exc.value.service_code == "1201"
    assert exc.value.message == "Invalid parameters"

def test_run_task_failed(service, mock_requests):
    """Test handling of failed tasks."""
    # Mock create task response
    create_response = MagicMock()
    create_response.ok = True
    create_response.json.return_value = {
        "data": {"task_id": "test_task_123"}
    }
    
    # Mock poll response with failure
    poll_response = MagicMock()
    poll_response.ok = True
    poll_response.json.return_value = {
        "data": {
            "task_status": "failed",
            "task_status_msg": "Generation failed"
        }
    }
    
    mock_requests.post.return_value = create_response
    mock_requests.get.return_value = poll_response
    
    with pytest.raises(Exception, match="Task failed: Generation failed"):
        service.run()

def test_get_result_with_metadata(service):
    """Test result retrieval with metadata."""
    service.result_url = "https://example.com/video.mp4"
    service.task_id = "test_task_123"
    service.created_at = 1234567890
    service.updated_at = 1234567891
    
    result = service.get_result()
    
    assert result["video_url"] == "https://example.com/video.mp4"
    assert result["task_id"] == "test_task_123"
    assert result["created_at"] == 1234567890
    assert result["updated_at"] == 1234567891 