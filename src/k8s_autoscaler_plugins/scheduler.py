from datetime import datetime
from importlib.metadata import entry_points

import kopf
import pluggy

from k8s_autoscaler_plugins.base import Nodepool
from k8s_autoscaler_plugins.const import PROJECT_NAME
from k8s_autoscaler_plugins.hooks import PluginHookSpec


class PluginScheduler:

    def __init__(self, logger: kopf.Logger):
        self.project_name = PROJECT_NAME
        self.last_run: datetime | None = None
        self.log = logger
        pm = pluggy.PluginManager(self.project_name)
        pm.add_hookspecs(PluginHookSpec)
        # Register installed plugins with entrypoints and instantiate them
        for ep in entry_points(group=PROJECT_NAME):
            plugin = ep.load()
            pm.register(plugin(), name=ep.name)
        self.pm = pm
        self.plugins = self.pm.get_plugins()
        if not self.plugins:
            raise kopf.PermanentError("No k8s autoscaler plugins registered.")
        else:
            self.log.info(f"Registered plugin packages: {[p.__module__ for p in self.plugins]}")

    def get_hooks(self, plugins: set, spec: kopf.Spec) -> list:
        names = [self.pm.get_name(plugin) for plugin in plugins]
        specs = [
            {name: spec.get("plugins", {}).get(name, {})} for name in names
        ]  # NOTE: npat spec plugin name must match registered plugin name
        caller = self.pm.hook.evaluate_nodepool  # TODO: make hook function name flexible
        hooks = caller.get_hookimpls()
        # Remove hooks for plugins with an empty spec # TODO: write test for this
        for s in specs:
            for k, v in s.items():
                if not v:
                    for hook in hooks:
                        if k == hook.plugin_name:
                            hooks.remove(hook)
        return hooks

    def schedule_target_min_node_count(self, nodepool: Nodepool, spec: kopf.Spec, logger: kopf.Logger) -> Nodepool:
        """
        Call plugin hooks and schedule target minimum node count to the maximum value over all plugins.
        """
        hooks = self.get_hooks(self.plugins, spec)
        results = []
        for hook in hooks:
            result = hook.function(nodepool=nodepool, spec=spec, logger=logger)
            if result >= 0:
                logger.info(f"[plugin] [{hook.plugin_name}] target_min_node_count={result}")
                results.append(result)
            else:
                logger.warning(f"[plugin] [{hook.plugin_name}] No target minimum node count scheduled")
        return max(results)
