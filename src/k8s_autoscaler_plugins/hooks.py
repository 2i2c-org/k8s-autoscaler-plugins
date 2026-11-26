"""
Define hook specs for autoscaler plugins using Pluggy.
"""

import kopf
import pluggy

from k8s_autoscaler_plugins.base import Nodepool
from k8s_autoscaler_plugins.const import PROJECT_NAME

hookspec = pluggy.HookspecMarker(PROJECT_NAME)
hookimpl = pluggy.HookimplMarker(PROJECT_NAME)


class PluginHookSpec:

    @hookspec
    def evaluate_nodepool(
        self,
        nodepool: Nodepool,
        spec: kopf.Spec,
        logger: kopf.Logger,
        args: dict | None = None,
    ):
        """
        Evaluate nodepool object and update target_min_node_count.
        """
