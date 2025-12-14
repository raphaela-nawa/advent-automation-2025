"""
day13_SCHEDULER_main.py

Prefect Cloud scheduler entrypoint for the Day 13 alert triage orchestrator.
Deploys a 15-minute cron schedule; run locally for testing.
"""

import os
import pathlib
import sys
from typing import Tuple

from prefect import flow, task
from prefect.client.schemas.schedules import CronSchedule
from prefect.deployments import Deployment

CURRENT_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from day13.day13_ORCHESTRATOR_alert_triage import day13_process_alerts


@task(name="day13_task_process_alerts", description="Ingest, dedup, classify, route alerts")
def day13_task_process_alerts() -> Tuple[int, int]:
    return day13_process_alerts()


@flow(name="day13_alert_triage_flow")
def day13_alert_triage_flow() -> Tuple[int, int]:
    return day13_task_process_alerts()


def day13_build_and_apply_deployment() -> None:
    """
    Build a Prefect deployment on a 15-minute schedule.
    """
    work_pool = os.getenv("DAY13_PREFECT_WORK_POOL", "default-agent-pool")
    deployment = Deployment.build_from_flow(
        flow=day13_alert_triage_flow,
        name="day13-alert-triage-15m",
        work_pool_name=work_pool,
        schedule=(CronSchedule(cron="*/15 * * * *", timezone="UTC")),
    )
    deployment.apply()


if __name__ == "__main__":
    day13_build_and_apply_deployment()
