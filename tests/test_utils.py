import os
import subprocess
import sys

from k8s_autoscaler_plugins.utils import get_plugin_manager


class TestPluginManager:

    def test_plugins_registered(self):
        """
        Test that the bundled plugins are registered from their entry points.
        """
        pm = get_plugin_manager()
        names = [pm.get_name(plugin) for plugin in pm.get_plugins()]
        assert 'always_on' in names

    def test_plugins_load_outside_repository(self, tmp_path):
        """
        Test that plugin entry points load when the repository root is not on `sys.path`..
        """
        env = {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}
        env['K8S_AUTOSCALER_PLUGINS_CLOUD_PROVIDER'] = 'TEST'
        code = (
            'from k8s_autoscaler_plugins.utils import get_plugin_manager\n'
            'pm = get_plugin_manager()\n'
            'print(",".join(sorted(pm.get_name(p) for p in pm.get_plugins())))\n'
        )
        result = subprocess.run(
            [sys.executable, '-c', code],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert 'always_on' in result.stdout.strip().split(',')
