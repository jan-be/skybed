from confluent_kafka import Producer

from skybed.message_types import UAV

producer: Producer


def publish_position_update(uav: UAV):
    producer.produce("updates", uav.model_dump_json())


def create_producer(ip: str):
    global producer
    producer = Producer({'bootstrap.servers': f"{ip}:9092"})
