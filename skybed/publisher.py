from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from datetime import datetime
import time
import json


def create_topic(topic_name):
    admin_client = AdminClient({'bootstrap.servers': 'localhost:9092'})  # NOTE: hardcoded credentials
    topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
    admin_client.create_topics([topic])


def create_producer():
    conf = {'bootstrap.servers': "localhost:9092"}
    producer = Producer(conf)
    return producer


def publish_messages(producer, interval, topic):
    message = {"origin": "mutate"}
    message_str = json.dumps(message)

    try:
        while True:
            producer.produce(topic, message_str.encode('utf-8'))
            producer.flush()  # Ensure message is sent
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            print(f'[{timestamp}] Published: {message_str}')
            time.sleep(interval)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    topic_name = 'releases'
    create_topic(topic_name)
    producer = create_producer()
    publish_messages(producer, interval=10, topic=topic_name)  # Sends the message every 10 seconds
