import docker

from skybed.message_types import UAVData

# Initialize the Docker client
client = docker.from_env()


def create_docker_network_and_container(uav_data: UAVData, kafka_ip) -> (str, str, str):
    name = f"UAV_{uav_data.uav_id}"
    net_name = f"net_{name}"

    network = client.networks.create(name=net_name, driver="bridge")

    uav_command = f'"{kafka_ip}" "{uav_data.uav_id}" "{uav_data.uav_type}" {uav_data.latitude} {uav_data.longitude} {uav_data.altitude} {uav_data.speed} {uav_data.direction} {uav_data.vertical_speed}'

    # TODO build the image
    # TODO consider creating seperate nets just for the uav_data

    container = client.containers.create(
        image="uav",
        name=name,
        command=uav_command,
        network=net_name
    )

    container.start()

    container.reload()  # Reload the container to update its network settings
    container_ip_address = container.attrs['NetworkSettings']['Networks'][net_name]['IPAddress']
    print(f"Container IP address in the network '{net_name}': {container_ip_address}")

    return network.id, container_ip_address, container.id


def remove_docker_network_and_container(network_id, container_id):
    network = client.networks.get(network_id)
    network.disconnect(container_id)
    network.remove()

    container = client.containers.get(container_id)
    container.stop(timeout=1)
    container.remove()

    print(f"Container {container_id} and network {network_id} removed.")
