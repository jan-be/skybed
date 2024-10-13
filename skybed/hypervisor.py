import asyncio
import concurrent.futures
import importlib
import inspect
import statistics
import threading
import time
from inspect import isclass
from time import sleep

import typer
from tqdm import tqdm
from typing_extensions import Annotated

from skybed import map_visualizer
from skybed.docker_handler import create_docker_network_and_container, remove_docker_network_and_container, \
    init_docker_networks, remove_docker_networks
from skybed.scenarios.base_scenario import Scenario
from skybed.uas_position_updater import loop_update_position_and_network_params, scenario, init_scenario, \
    errors_to_success

typer_app = typer.Typer()

starting_time: float


async def stop_after_time(seconds: float):
    await asyncio.sleep(seconds)
    raise KeyboardInterrupt()


@typer_app.command()
def main(scenario_file: Annotated[str, typer.Argument()] = "schoenhagen_near_collision",
         kafka_ip: Annotated[str, typer.Argument()] = "localhost"):
    async def _main():
        # grab the first class instance that is a subclass of Scenario
        scenario_module = importlib.import_module(f"skybed.scenarios.{scenario_file}")
        scenario: Scenario = \
            inspect.getmembers(scenario_module, lambda c: isclass(c) and c != Scenario and issubclass(c, Scenario))[0][
                1]()

        print(scenario)

        init_docker_networks()

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                # Submit all tasks to the executor
                futures = [executor.submit(create_docker_network_and_container, uav, kafka_ip) for uav in scenario.uavs]

                # add progress bar
                with tqdm(total=len(scenario.uavs)) as pbar:
                    # Wait for all threads to complete
                    for future in concurrent.futures.as_completed(futures):
                        future.result()
                        pbar.update(1)

            sleep(4)
            init_scenario(scenario)

            global starting_time
            starting_time = time.perf_counter()

            await asyncio.gather(
                loop_update_position_and_network_params(),
                map_visualizer.run_map_server(),
                stop_after_time(15 * 60)
            )

        except KeyboardInterrupt:
            print("Ctrl+C detected!")
        finally:
            cleanup()

    asyncio.run(_main())


def cleanup():
    print("Performing cleanup")

    print("error rates:", errors_to_success)

    with open('repeatability_results.json', 'a') as file:
        file.write(f"{[x.position for x in scenario.uavs]}\n")

    print([x.evaluation.network_update_count for x in scenario.uavs])
    avg_network_update_count = statistics.mean([x.evaluation.network_update_count for x in scenario.uavs])
    avg_network_update_time = (time.perf_counter() - starting_time) / avg_network_update_count
    with open('avg_network_update_time.csv', 'a') as file:
        file.write(f"{avg_network_update_time}\n")

    threads = []
    for uav in scenario.uavs:
        # stop always takes 1 second, so multithreading this makes a difference
        thread = threading.Thread(target=remove_docker_network_and_container, args=[uav.container])
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    remove_docker_networks()


if __name__ == '__main__':
    typer_app()
