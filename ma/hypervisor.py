import threading
from time import sleep

from ma import map_visualizer
from ma.docker_networks import create_and_attach_docker_network, destroy_docker_network
from ma.subscriber import subscribe
from ma.uas_position_updater import loop_update_post_position, uavs_data

uav_net_map = {}


def cleanup():
    print("Performing cleanup")
    for uav_data in uavs_data:
        destroy_docker_network(uav_net_map[uav_data.uav_id]['network_id'])


if __name__ == '__main__':
    try:
        for uav_data in uavs_data:
            network_id, ip = create_and_attach_docker_network(f"UAV_{uav_data.uav_id}")
            uav_net_map[uav_data.uav_id] = {"network_id": network_id, "ip": ip}
            threading.Thread(target=subscribe, args=[ip, uav_data.uav_id]).start()

        threading.Thread(target=loop_update_post_position, args=[uav_net_map]).start()

        map_visualizer.run_map_server_async()

        # keep cleanup from being called right away
        while True:
            sleep(1)

    except KeyboardInterrupt:
        print("Ctrl+C detected!")
    finally:
        cleanup()
