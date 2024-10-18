import os
import statistics
import time
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from skybed.message_types import UAV
from skybed.scenarios.base_scenario import Scenario
from skybed.uas_position_updater import errors_to_success

starting_time: float


class SkybedLogFile(BaseModel):
    avg_network_update_count: float
    avg_network_update_time: float
    uavs_final_state: list[UAV]
    position_req_successes: int
    position_req_errors: int


def init_logging():
    global starting_time
    starting_time = time.perf_counter()


def write_logs(scenario: Scenario):
    avg_network_update_count = statistics.mean([x.evaluation.network_update_count for x in scenario.uavs])

    # don't throw an error at 0, just return 0
    avg_network_update_time = (time.perf_counter() - starting_time) / avg_network_update_count \
        if avg_network_update_count else 0

    log_file = SkybedLogFile(
        avg_network_update_count=avg_network_update_count,
        avg_network_update_time=avg_network_update_time,
        uavs_final_state=scenario.uavs,
        position_req_successes=errors_to_success["Success"],
        position_req_errors=errors_to_success["TimeoutError"])

    # create the logs directory in the main repo directory if it doesn't exist and put the JSON into it
    Path(os.path.join(os.path.dirname(__file__), "../logs")).mkdir(parents=True, exist_ok=True)
    with open(f"{os.path.join(os.path.dirname(__file__), "../logs")}/log_{datetime.now().isoformat()}.json", "w+") as f:
        f.write(log_file.model_dump_json())
