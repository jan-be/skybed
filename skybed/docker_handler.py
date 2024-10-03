import threading

import docker

from skybed.message_types import UAV, UAVContainer

# Initialize the Docker client
client = docker.from_env()


def create_docker_networks():
    client.networks.create(name="skybed-throttled-net", driver="bridge")
    client.networks.create(name="skybed-unthrottled-net", internal=True)


def create_docker_network_and_container(uav: UAV, kafka_ip):
    name = f"UAV_{uav.uav_id}"
    throttled_network = client.networks.get("skybed-throttled-net")
    unthrottled_network = client.networks.get("skybed-unthrottled-net")

    # replace kafka IP with the gateway of the throttled network, if on the same PC
    if kafka_ip == "localhost":
        kafka_ip = throttled_network.attrs["IPAM"]["Config"][0]["Gateway"]

    uav_command = f'"{kafka_ip}" "{uav.uav_id}" "{uav.uav_type}" -- {uav.latitude} {uav.longitude} {uav.altitude} {uav.speed} {uav.direction} {uav.vertical_speed}'

    container = client.containers.create(
        image="uav",
        name=name,
        command=uav_command,
        network=throttled_network.name,
        auto_remove=True
    )

    unthrottled_network.connect(container)

    container.start()

    container.reload()  # Reload the container to update its network settings
    throttled_ip_address = container.attrs['NetworkSettings']['Networks'][throttled_network.name]['IPAddress']
    unthrottled_ip_address = container.attrs['NetworkSettings']['Networks'][unthrottled_network.name]['IPAddress']
    print(
        f"Container {uav.uav_id} IP addresses: throttled: {throttled_ip_address}, not throttled: {unthrottled_ip_address}")

    uav.container = UAVContainer(id=container.id, throttled_ip=throttled_ip_address,
                                 unthrottled_ip=unthrottled_ip_address, throttled_network_id=throttled_network.id,
                                 unthrottled_network_id=unthrottled_network.id)

    threading.Thread(target=print_container_output, args=[uav], daemon=True).start()


def print_container_output(uav: UAV):
    container = client.containers.get(uav.container.id)

    output = container.attach(stdout=True, stream=True, logs=True)
    # this works indefinitely because idk
    for line in output:
        print(f"Docker UAV {uav.uav_id}: {str(line, 'utf-8')}", end='')


def remove_docker_network_and_container(uav_container: UAVContainer):
    container = client.containers.get(uav_container.id)
    container.stop(timeout=1)

    print(f"Container {uav_container.id} stopped.")


def remove_docker_networks():
    client.networks.get("skybed-throttled-net").remove()
    client.networks.get("skybed-unthrottled-net").remove()
    print("Networks removed")
