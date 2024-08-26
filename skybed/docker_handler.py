import threading

import docker

from skybed.message_types import UAVData, UAVContainer

# Initialize the Docker client
client = docker.from_env()


def create_docker_network_and_container(uav_data: UAVData, kafka_ip):
    name = f"UAV_{uav_data.uav_id}"
    net_throttled_name = f"net_throttled_{name}"
    net_unthrottled_name = f"net_unthrottled_{name}"

    throttled_network = client.networks.create(name=net_throttled_name, driver="bridge")
    unthrottled_network = client.networks.create(name=net_unthrottled_name, internal=True)

    # replace kafka IP with the gateway of the throttled network, if on the same PC
    if kafka_ip == "localhost":
        kafka_ip = throttled_network.attrs["IPAM"]["Config"][0]["Gateway"]

    uav_command = f'"{kafka_ip}" "{uav_data.uav_id}" "{uav_data.uav_type}" {uav_data.latitude} {uav_data.longitude} {uav_data.altitude} {uav_data.speed} {uav_data.direction} {uav_data.vertical_speed}'

    container = client.containers.create(
        image="uav",
        name=name,
        command=uav_command,
        network=net_throttled_name,
        auto_remove=True
    )

    unthrottled_network.connect(container)

    container.start()

    container.reload()  # Reload the container to update its network settings
    throttled_ip_address = container.attrs['NetworkSettings']['Networks'][net_throttled_name]['IPAddress']
    unthrottled_ip_address = container.attrs['NetworkSettings']['Networks'][net_unthrottled_name]['IPAddress']
    print(
        f"Container IP addresses in the network '{net_throttled_name}': throttled: {throttled_ip_address} not throttled: {unthrottled_ip_address}")

    uav_data.container = UAVContainer(id=container.id, throttled_ip=throttled_ip_address,
                                      unthrottled_ip=unthrottled_ip_address, throttled_network_id=throttled_network.id,
                                      unthrottled_network_id=unthrottled_network.id)

    threading.Thread(target=print_container_output, args=[uav_data], daemon=True).start()


def print_container_output(uav_data: UAVData):
    container = client.containers.get(uav_data.container.id)

    output = container.attach(stdout=True, stream=True, logs=True)
    # this works indefinitely because idk
    for line in output:
        print(f"Docker UAV {uav_data.uav_id}: {str(line, "utf-8")}", end='')

def remove_docker_network_and_container(uav_container: UAVContainer):
    for net_id in [uav_container.throttled_network_id, uav_container.unthrottled_network_id]:
        network = client.networks.get(net_id)
        network.disconnect(uav_container.id)
        network.remove()

    container = client.containers.get(uav_container.id)
    container.stop(timeout=1)

    print(f"Container {uav_container.id} stopped and networks removed.")
