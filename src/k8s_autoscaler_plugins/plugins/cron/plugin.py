import datetime
import kopf
from cron_converter import Cron
from k8s_autoscaler_plugins.base import Nodepool
from k8s_autoscaler_plugins.hooks import hookimpl


class CronPlugin:

    def __init__(self):
        self.schedule_list = []

    @hookimpl
    def evaluate_nodepool(self, nodepool: Nodepool, spec: kopf.Spec, logger: kopf.Logger, args: dict | None = None) -> int:
        if not self.schedule_list:
            # One-time set up of cron schedules using a reference time when first called
            self.spec_list =  spec.get('plugins', {}).get('cron', {}).get('jobs', [])
            cron_instance = Cron()
            reference = datetime.datetime.now(datetime.UTC) # TODO: add support for timezone aware schedules
            for spec in self.spec_list:
                minimum = spec.get('minimum', 0) # TODO: spec validation
                cron_instance.from_string(spec.get('schedule', ''))
                schedule = cron_instance.schedule(reference)
                next_time = next(schedule)
                self.schedule_list.append({'minimum': minimum, 'schedule': schedule, 'next_time': next_time})
        else:
            for s in self.schedule_list:
                now_time = datetime.datetime.now(datetime.UTC) 
                if now_time > s['next_time']:  
                    if nodepool.target_min_node_count <= s['minimum']:
                        target_min_node_count = s['minimum']
                        logger.info(f"[plugin] {__package__} triggered for scheduled time {s['next_time']}")
                    next_time = next(s['schedule'])
                    s['next_time'] = next_time
                else:
                    target_min_node_count = nodepool.target_min_node_count
                logger.debug(f'{s['next_time']=}')
            logger.debug(f'[plugin] {__package__} succeeded')
            return target_min_node_count
