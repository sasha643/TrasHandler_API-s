from confluent_kafka import Producer
import json

# Kafka Producer configuration for Confluent Kafka
conf = {
    'bootstrap.servers': '13.232.64.63:9092',  # Kafka broker address
    'client.id': 'vendor-location-producer',  # Client identifier for the producer
    'acks': 'all',  # Wait for acknowledgment from all replicas
}

# Initialize the Confluent Kafka Producer
producer = Producer(conf)

def delivery_report(err, msg):
    """
    Callback to report the delivery status of the message.
    This function will be called once the message is successfully delivered or if delivery fails.
    """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [partition: {msg.partition()}] @ offset {msg.offset()}")

def send_location_update(action, data, vendor_id):
    """
    Sends a location update message to Kafka.

    :param action: The action being performed (e.g., update, delete)
    :param data: The location data or any other data payload
    :param vendor_id: Unique identifier of the vendor
    """
    data_with_action = {
        'action': action,
        'vendor_id': vendor_id,
        'data': data
    }

    # Log the data being sent
    print(f"Sending to Kafka: {json.dumps(data_with_action, indent=4)}")

    try:
        # Produce the message to Kafka
        producer.produce(
            topic='vendor-location-topic',  # Kafka topic name
            value=json.dumps(data_with_action),  # Convert the message to a JSON string
            callback=delivery_report  # Callback to confirm success or failure
        )
        # Wait for any outstanding messages to be delivered
        producer.flush()
    except Exception as e:
        print(f"Failed to send message: {e}")
