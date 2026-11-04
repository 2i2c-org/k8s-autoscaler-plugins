import datetime
import kopf
from cron_converter import Cron
from typing import Any
from k8s_autoscaler_plugins.base import Nodepool
from k8s_autoscaler_plugins.hooks import hookimpl

class CronPlugin:

    def __init__(self):
        self.hello = 'hello world'
        self.last_run = None

    @hookimpl
    def evaluate_nodepool(self, nodepool: Nodepool, spec: kopf.Spec, logger: kopf.Logger, args: dict | None = None) -> Nodepool:
        # TODO: incomplete
        target_min_node_count = spec.get('plugins', {}).get('cron', {}).get('minimum', 0)
        if args:
            self.last_run = args['last_run']
            logger.warning(f'{self.last_run=}')
            logger.warning(f'{self.hello=}')
        else:
            raise kopf.TemporaryError(f'[plugin] {self.__module__} Could not determine `last_run` time')
        # cron_instance = Cron()
        # schedule_list =  spec.get('plugins', {}).get('cron', {}).get('schedule', [])
        # for schedule in schedule_list:
        #     logger.debug(f'{schedule=}')
        #     cron_instance.from_string(schedule)
        #     now_time = datetime.datetime.now(datetime.UTC)
        #     next_time = next(cron_schedule)
        #     if next_time < datetime.datetime.now(datetime.UTC):  # TODO: add support for timezone aware schedules
        #         if nodepool.target_min_node_count <= target_min_node_count:
        #             nodepool.target_min_node_count = target_min_node_count
        logger.debug(f'[plugin] {__package__} succeeded')
        return nodepool
