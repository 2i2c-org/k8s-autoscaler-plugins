import kopf
import pluggy
from datetime import datetime
from k8s_autoscaler_plugins.base import Nodepool
import k8s_autoscaler_plugins.hooks as hookspec


class PluginScheduler:

    def __init__(self):
        self.project_name = "k8s-autoscaler-plugins"
        self.last_run: datetime | None = None
        pm = pluggy.PluginManager(self.project_name)
        pm.add_hookspecs(hookspec)
        # Automatically register installed plugins with plugin entrypoint
        pm.load_setuptools_entrypoints(self.project_name)
        self.pm = pm

    def get_prioritized_hooks(self, specs: list[kopf.Spec]) -> dict:
        priorities = {}
        for s in specs:
            for k, v in s.items():
                priorities.update({k: v.get('priority', None)})
        caller = self.pm.hook.evaluate_nodepool # TODO: make hook function name flexible
        hooks = sorted(
            caller.get_hookimpls(),
            key = lambda impl: priorities[impl.plugin_name],  # TODO: validate spec to ensure unique priority ordering
            reverse=True  
        )
        return hooks

    def set_target_min_node_count(self, nodepool: Nodepool, spec: kopf.Spec, logger: kopf.Logger):
        """
        Calculate and set nodepool target minimum node count by calling plugin hook implementation functions in reverse priority order, i.e. highest priority functions override the final results and are called last.
        """
        plugins = self.pm.get_plugins()
        if not plugins:
            raise kopf.PermanentError('No k8s autoscaler plugins registered.')
        else:
            logger.info(f'Registered plugin packages: {[p.__package__ for p in plugins]}')
        names = [self.pm.get_name(plugin) for plugin in plugins]
        specs = [{name: spec.get('plugins', {}).get(name, {})} for name in names] # NOTE: npat spec plugin name must match registered plugin name
        hooks = self.get_prioritized_hooks(specs)
        results = []
        for hook in hooks:
            result = hook.function(nodepool=nodepool, spec=spec, logger = logger) # NOTE: assumes every plugin handler has the same call signature
            results.append(result)
            logger.info(f'[plugin] [{hook.plugin_name}] {result.target_min_node_count=}')
        self.last_run = datetime.now()
        return results.pop()
