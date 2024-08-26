from confluent_kafka import Producer

from skybed.message_types import UAVData

producer: Producer


def publish_position_update(uav_data: UAVData):
    producer.produce("update", uav_data.model_dump_json())


def create_producer(ip: str):
    global producer
    producer = Producer({'bootstrap.servers': f"{ip}:9092"})
