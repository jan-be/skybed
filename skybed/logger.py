import os
import statistics
import time
from datetime import datetime
from pathlib import Path

import psutil
from pydantic import BaseModel, ConfigDict

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
    iso_time_str: str
    uavs: list[UAV]
    total_runtime: float
    cpu_usage: float
    memory_usage: float

    model_config = ConfigDict(arbitrary_types_allowed=True)


def init_logging():
    global starting_time
    starting_time = time.perf_counter()


def write_logs(scenario: Scenario):
    total_runtime = time.perf_counter() - starting_time

    avg_network_update_count = statistics.mean([x.evaluation.network_update_count for x in scenario.uavs])

    # don't throw an error at 0, just return 0
    avg_network_update_time = total_runtime / avg_network_update_count if avg_network_update_count else 0

    iso_time_str = datetime.now().isoformat()

    log_file = SkybedLogFile(
        avg_network_update_count=avg_network_update_count,
        avg_network_update_time=avg_network_update_time,
        uavs_final_state=scenario.uavs,
        position_req_successes=errors_to_success["Success"],
        position_req_errors=errors_to_success["TimeoutError"],
        iso_time_str=iso_time_str,
        uavs=scenario.uavs,
        total_runtime=total_runtime,
        cpu_usage=psutil.getloadavg()[1],
        memory_usage=psutil.virtual_memory().used
    )

    # create the logs directory in the main repo directory if it doesn't exist and put the JSON into it
    Path(os.path.join(os.path.dirname(__file__), "../logs")).mkdir(parents=True, exist_ok=True)
    with open(f"{os.path.join(os.path.dirname(__file__), '../logs')}/log_{iso_time_str}.json", "w+") as f:
        f.write(log_file.model_dump_json())
