import logging
import os
import subprocess
import sys

from k8s_autoscaler_plugins.utils import PluginScheduler


class TestPluginManager:

    def test_plugins_registered(self):
        """
        Test that the bundled plugins are registered from their entry points.
        """
        scheduler = PluginScheduler(logger=logging.getLogger(__name__))
        names = [scheduler.pm.get_name(plugin) for plugin in scheduler.plugins]
        assert "always_on" in names
        assert "cron" in names

    def test_plugins_load_outside_repository(self, tmp_path):
        """
        Test that plugin entry points load when the repository root is not on `sys.path`..
        """
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        env["K8S_AUTOSCALER_PLUGINS_CLOUD_PROVIDER"] = "TEST"
        code = (
            "import logging\n"
            "from k8s_autoscaler_plugins.utils import PluginScheduler\n"
            "scheduler = PluginScheduler(logger=logging.getLogger())\n"
            'print(",".join(sorted(scheduler.pm.get_name(p) for p in scheduler.plugins)))\n'
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        names = result.stdout.strip().split(",")
        assert "always_on" in names
        assert "cron" in names
