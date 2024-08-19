import threading

from ma import map_visualizer
from ma.docker_networks import create_and_attach_docker_network, destroy_docker_network
from ma.subscriber import subscribe
from ma.uas_position_updater import loop_update_post_position, uavs_data

uav_net_map = {}


def cleanup():
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
    except KeyboardInterrupt:
        print("\nCtrl+C detected!")
    finally:
        # cleanup()
        pass
