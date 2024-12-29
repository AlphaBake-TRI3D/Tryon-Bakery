"""Virtual try-on services."""

from ..factory import ServiceFactory, ServiceType
from .fashnai import FashnaiVTON
from .klingai import KlingaiVTON
from .replicate import ReplicateVTON
from .vmodel import VModelVTON

# Register VTON services
ServiceFactory.register(ServiceType.VTON, "fashnai", FashnaiVTON)
ServiceFactory.register(ServiceType.VTON, "klingai", KlingaiVTON)
ServiceFactory.register(ServiceType.VTON, "replicate", ReplicateVTON)
ServiceFactory.register(ServiceType.VTON, "vmodel", VModelVTON) 