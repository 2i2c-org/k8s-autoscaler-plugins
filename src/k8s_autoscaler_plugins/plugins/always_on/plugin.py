import kopf
from typing import Any
from k8s_autoscaler_plugins.base import Nodepool
from k8s_autoscaler_plugins.hooks import hookimpl

class AlwaysOnPlugin:

    @hookimpl
    def evaluate_nodepool(self, nodepool: Nodepool, spec: kopf.Spec, logger: kopf.Logger, **_: Any) -> Nodepool:
        target_min_node_count = spec.get('plugins', {}).get('always_on', {}).get('minimum', 0)
        logger.debug(f'[plugin] {self.__module__} succeeded')
        return target_min_node_count
