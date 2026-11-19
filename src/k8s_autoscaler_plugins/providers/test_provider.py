from __future__ import annotations
import kopf
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from k8s_autoscaler_plugins.base import Nodepool
from k8s_autoscaler_plugins.providers.base import CloudProvider

class TestProvider(CloudProvider):
    """
    No-op cloud provider for testing and mocking.
    """
    def __init__(self, logger: kopf.Logger | None = None):
        super().__init__(logger=logger)
        self._entered = False
        self._exited = False

    async def __aenter__(self):
        self._entered = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._exited = True

    async def get_nodepool(self, name: str, zone: str | None = None, region: str | None = None) -> dict:
        data = {
            'name': name,
            'min_node_count': 0,
            'max_node_count': 2
        }
        return data

    async def list_nodepool(self, label_selector: str = '', zone: str | None = None, region: str | None = None) -> list[dict]:
        return []

    async def set_min_node_count(self, nodepool: Nodepool) -> None:
        ...
