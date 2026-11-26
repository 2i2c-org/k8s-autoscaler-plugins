import datetime

import kopf
from cron_converter import Cron

from k8s_autoscaler_plugins.base import Nodepool
from k8s_autoscaler_plugins.hooks import hookimpl


class CronPlugin:

    def __init__(self):
        self.plugin_name = "cron"
        self.schedule_list = []

    @hookimpl
    def evaluate_nodepool(
        self,
        nodepool: Nodepool,
        spec: kopf.Spec,
        logger: kopf.Logger,
        args: dict | None = None,
    ) -> int:
        if not self.schedule_list:
            # One-time set up of cron schedules using a reference time when first called
            self.spec_list = spec.get("plugins", {}).get("cron", {}).get("jobs", [])
            reference = datetime.datetime.now(datetime.UTC)  # TODO: add support for timezone aware schedules
            for spec in self.spec_list:
                minimum = spec.get("minimum", 0)  # TODO: spec validation
                cron_instance = Cron()
                cron_instance.from_string(spec.get("schedule", ""))
                schedule = cron_instance.schedule(reference)
                next_time = next(schedule)
                self.schedule_list.append({"minimum": minimum, "schedule": schedule, "next_time": next_time})
                logger.debug(
                    f"[plugin] [{self.plugin_name}] Initialised job {schedule.cron.to_string()}: target_min_node_count={minimum} at {next_time}"
                )
            return nodepool.target_min_node_count
        else:
            now_time = datetime.datetime.now(datetime.UTC)
            for s in self.schedule_list:
                if now_time > s["next_time"]:
                    target_min_node_count = s["minimum"]
                    logger.debug(
                        f"[plugin] [{self.plugin_name}] triggered to target_min_node_count={target_min_node_count} on job {s['schedule'].cron.to_string()} for scheduled time {s['next_time']}"
                    )
                    next_time = next(s["schedule"])
                    s["next_time"] = next_time
                    return target_min_node_count  # break loop to avoid more than one schedule overriding each other # TODO: validate schedule precedence?
                else:
                    target_min_node_count = nodepool.target_min_node_count
                    return target_min_node_count
        return 0
