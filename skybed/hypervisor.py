import asyncio
import concurrent.futures
import importlib
import inspect
import threading
from inspect import isclass

import typer
from tqdm import tqdm
from typing_extensions import Annotated

from skybed.docker_handler import create_docker_network_and_container, remove_docker_network_and_container, \
    init_docker_networks, remove_docker_networks
from skybed.logger import init_logging, write_logs
from skybed.map_visualizer import run_map_server_thread
from skybed.scenarios.base_scenario import Scenario
from skybed.uas_position_updater import loop_update_position, scenario, init_scenario, loop_update_network_params

typer_app = typer.Typer()


async def stop_after_time(seconds: float):
    await asyncio.sleep(seconds)
    raise KeyboardInterrupt()


@typer_app.command()
def main(scenario_file: Annotated[str, typer.Argument()] = "schoenhagen_near_collision",
         test_system_ip: Annotated[str, typer.Argument()] = "localhost"):
    async def _main():
        # grab the first class instance that is a subclass of Scenario
        scenario_module = importlib.import_module(f"skybed.scenarios.{scenario_file}")
        scenario_start: Scenario = \
            inspect.getmembers(scenario_module, lambda c: isclass(c) and c != Scenario and issubclass(c, Scenario))[0][
                1]()

        print(scenario_start)

        init_docker_networks()

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                # Submit all tasks to the executor
                futures = [executor.submit(create_docker_network_and_container, uav, test_system_ip) for uav in scenario_start.uavs]

                # add progress bar
                with tqdm(total=len(scenario_start.uavs)) as pbar:
                    # Wait for all threads to complete
                    for future in concurrent.futures.as_completed(futures):
                        future.result()
                        pbar.update(1)

            init_scenario(scenario_start)

            init_logging()

            try:
                await asyncio.gather(
                    loop_update_position(),
                    loop_update_network_params(),
                    asyncio.to_thread(run_map_server_thread),
                    stop_after_time(10 * 60)
                )
            except Exception as e:
                print(e)

        except KeyboardInterrupt:
            print("Ctrl+C detected!")
        finally:
            cleanup()

    asyncio.run(_main())


def cleanup():
    print("Performing cleanup")

    write_logs(scenario)

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
