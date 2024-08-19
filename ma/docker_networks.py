import docker
import docker.errors

def create_and_attach_docker_network(network_name: str) -> (str, str):
    # Initialize the Docker client
    client = docker.from_env()

    try:
        # Create a new network
        network = client.networks.create(name=network_name, driver="bridge")
        print(f"Network '{network_name}' created successfully with ID: {network.id}")

        # Get the container by name
        container = client.containers.get("docker-kafka-1")

        # Connect the container to the network
        network.connect(container)
        print(f"Container 'docker-kafka-1' connected to network '{network_name}'.")

        # Retrieve the IP address of the container in the network
        container.reload()  # Reload the container to update its network settings
        network_settings = container.attrs['NetworkSettings']['Networks']
        container_ip_address = network_settings[network_name]['IPAddress']
        print(f"Container IP address in the network '{network_name}': {container_ip_address}")

        # Return the network ID and the container's IP address
        return network.id, container_ip_address

    except docker.errors.NotFound as e:
        print(f"Error: {str(e)}")
    except docker.errors.APIError as e:
        print(f"Docker API Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        client.close()


def destroy_docker_network(network_id):
    # Initialize the Docker client
    client = docker.from_env()

    try:
        # Get the network by ID
        network = client.networks.get(network_id)

        # Disconnect all containers from the network
        connected_containers = network.attrs['Containers']
        for container_id in connected_containers:
            network.disconnect(container_id)
            print(f"Disconnected container with ID '{container_id}' from network '{network_id}'.")

        # Remove (destroy) the network
        network.remove()
        print(f"Network with ID '{network_id}' removed successfully.")

    except docker.errors.NotFound as e:
        print(f"Error: Network with ID '{network_id}' not found.")
    except docker.errors.APIError as e:
        print(f"Docker API Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        client.close()
