import importlib
import inspect
import threading
from inspect import isclass
from time import sleep

import typer
from typing_extensions import Annotated

from skybed import map_visualizer
from skybed.docker_handler import create_docker_network_and_container, remove_docker_network_and_container, \
    create_docker_networks, remove_docker_networks
from skybed.scenarios.base_scenario import Scenario
from skybed.uas_position_updater import loop_update_position_and_network_params, uavs, init_scenario

typer_app = typer.Typer()


@typer_app.command()
def main(scenario_file: Annotated[str, typer.Argument()] = "schoenhagen_near_collision",
         kafka_ip: Annotated[str, typer.Argument()] = "localhost"):
    # grab the first class instance that is a subclass of Scenario
    scenario_module = importlib.import_module(f"skybed.scenarios.{scenario_file}")
    scenario: Scenario = \
    inspect.getmembers(scenario_module, lambda c: isclass(c) and c != Scenario and issubclass(c, Scenario))[0][1]()

    print(scenario)

    create_docker_networks()

    try:
        docker_starting_threads = []

        for uav in scenario.uavs:
            thread = threading.Thread(target=create_docker_network_and_container, args=[uav, kafka_ip])
            docker_starting_threads.append(thread)
            thread.start()

        for thread in docker_starting_threads:
            thread.join()

        sleep(4)
        init_scenario(scenario)
        threading.Thread(target=loop_update_position_and_network_params, daemon=True).start()

        map_visualizer.run_map_server_async()

        # keep cleanup from being called right away
        while True:
            sleep(1)

    except KeyboardInterrupt:
        print("Ctrl+C detected!")
    finally:
        cleanup()


def cleanup():
    print("Performing cleanup")
    threads = []
    for uav in uavs:
        # stop always takes 1 second, so multithreading this makes a difference
        thread = threading.Thread(target=remove_docker_network_and_container, args=[uav.container])
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    remove_docker_networks()


if __name__ == '__main__':
    typer_app()
