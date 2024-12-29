"""Video generation services."""

from ...types.video import VideoModelVersion
from ..factory import ServiceFactory, ServiceType
from .kling import KlingVideoGen

# Register Kling video services
ServiceFactory.register(ServiceType.VIDEO, VideoModelVersion.KLING_V1.value, KlingVideoGen)
ServiceFactory.register(ServiceType.VIDEO, VideoModelVersion.KLING_V1_5.value, KlingVideoGen) 