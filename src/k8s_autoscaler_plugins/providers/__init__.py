import kopf

from k8s_autoscaler_plugins.providers.base import CloudProvider
from k8s_autoscaler_plugins.providers.test_provider import TestProvider

__all__ = ["CloudProvider", "TestProvider", "create_provider"]


def create_provider(name: str, logger: kopf.Logger | None = None) -> CloudProvider:
    if name == "GCP":
        from k8s_autoscaler_plugins.providers.gcp import GCPProvider

        return GCPProvider(logger=logger)
    elif name == "TEST":
        return TestProvider(logger=logger)
    else:
        raise ValueError(f"Provider name '{name}' not recognized.")
