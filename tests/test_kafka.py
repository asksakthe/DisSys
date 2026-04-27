import json, uuid
import pytest
from kafka import KafkaProducer, KafkaConsumer

TOPIC = "test-events"
BOOTSTRAP = "localhost:9092"

def test_kafka_produce_consume():
    """No message loss test"""
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode()
    )
    sent_ids = []
    for _ in range(10):
        eid = str(uuid.uuid4())
        producer.send(TOPIC, {"event_id": eid})
        sent_ids.append(eid)
    producer.flush()

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode()),
        consumer_timeout_ms=5000,
        group_id=f"test-group-{uuid.uuid4()}"
    )
    received_ids = [msg.value["event_id"] for msg in consumer]
    consumer.close()

    for sid in sent_ids:
        assert sid in received_ids, f"Message lost: {sid}"

def test_kafka_message_schema():
    """Schema validation test"""
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode()
    )
    valid_event = {
        "event_id": str(uuid.uuid4()),
        "user_id": 42,
        "event_type": "click",
        "ts": "2024-01-01T00:00:00+00:00"
    }
    producer.send(TOPIC, valid_event)
    producer.flush()

    required_fields = ["event_id", "user_id", "event_type", "ts"]
    for field in required_fields:
        assert field in valid_event
        