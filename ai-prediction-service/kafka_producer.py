import json
from kafka import KafkaProducer
from config import KAFKA_BOOTSTRAP_SERVERS


def make_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        key_serializer=lambda k: k.encode("utf-8"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def publish_event(producer: KafkaProducer, topic: str, key: str, event_dict: dict):
    producer.send(topic, key=key, value=event_dict)
    producer.flush()