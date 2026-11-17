from __future__ import annotations
import kopf
import logging
from abc import ABC, abstractmethod
from types import TracebackType
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from k8s_autoscaler_plugins.base import Nodepool

class CloudProvider(ABC):
    """
    Abstract base class with Kubernetes API methods and standardizes the construction of all cloud providers (see https://peps.python.org/pep-3119/).
    """
    def __init__(self, logger: kopf.Logger | None = None, timeout: int = 300, interval: int = 10):
        if logger:
            self.log = logger
        else:
            self.log = logging.getLogger(__name__)

    @abstractmethod
    async def __aenter__(self):
        ... # Note that `...` is a Python placeholder object

    @abstractmethod
    async def __aexit__(self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None):
        ...

    @abstractmethod
    async def get_nodepool(self, name: str, zone: str | None = None, region: str | None = None) -> dict:
        ...

    @abstractmethod
    async def list_nodepool(self, label_selector: str = '', zone: str | None = None, region: str | None = None) -> list[dict]:
        ...

    @abstractmethod
    async def set_min_node_count(self, nodepool: Nodepool) -> None:
        ...
