import threading
from time import sleep

import typer

from skybed import map_visualizer
from skybed.docker_handler import create_docker_network_and_container, remove_docker_network_and_container
from skybed.uas_position_updater import loop_update_position_and_network_params, uavs_data

uav_net_map = {}

typer = typer.Typer()


@typer.command()
def main(kafka_ip: str = "172.17.0.1"):
    try:
        for uav_data in uavs_data:
            network_id, ip, container_id = create_docker_network_and_container(uav_data, kafka_ip)
            uav_net_map[uav_data.uav_id] = {"network_id": network_id, "ip": ip, "container_id": container_id}

        sleep(4)
        threading.Thread(target=loop_update_position_and_network_params, args=[uav_net_map]).start()

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
        remove_docker_network_and_container(uav_net_map[uav_data.uav_id]['network_id'],
                                            uav_net_map[uav_data.uav_id]['container_id'])


if __name__ == '__main__':
    typer()
