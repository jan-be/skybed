# TODO this is unmodified chatGPT code

import docker

def get_container_ip(container_name):
    # Initialize Docker client
    client = docker.from_env()

    try:
        # Find the container by name
        container = client.containers.get(container_name)

        # Get the container's network settings
        network_settings = container.attrs['NetworkSettings']

        print(network_settings)

        # Extract IP addresses and bridge interface names
        network_info = {}
        for network_name, settings in network_settings['Networks'].items():
            # Get the network details to find the network ID
            network = client.networks.get(network_name)
            network_id = network.id
            # Construct the bridge interface name (Docker uses "br-" prefix followed by the first 12 characters of the network ID)
            bridge_name = f"br-{network_id[:12]}"

            network_info[network_name] = {
                "IPAddress": settings['IPAddress'],
                "BridgeInterface": bridge_name
            }

        return network_info

    except docker.errors.NotFound:
        return f"Container '{container_name}' not found."
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    # Example usage
    container_name = "docker-kafka-1"
    ip_addresses = get_container_ip(container_name)
    print(ip_addresses)
