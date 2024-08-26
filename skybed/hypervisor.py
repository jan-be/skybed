import threading
from time import sleep

import typer

from skybed import map_visualizer
from skybed.docker_handler import create_docker_network_and_container, remove_docker_network_and_container
from skybed.uas_position_updater import loop_update_position_and_network_params, uavs_data

typer = typer.Typer()


@typer.command()
def main(kafka_ip: str = "localhost"):
    try:
        docker_starting_threads = []

        for uav_data in uavs_data:
            thread = threading.Thread(target=create_docker_network_and_container, args=[uav_data, kafka_ip])
            docker_starting_threads.append(thread)
            thread.start()

        for thread in docker_starting_threads:
            thread.join()

        sleep(4)
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
    for uav_data in uavs_data:
        # stop always takes 1 second, so multithreading this makes a difference
        threading.Thread(target=remove_docker_network_and_container, args=[uav_data.container]).start()


if __name__ == '__main__':
    typer()
