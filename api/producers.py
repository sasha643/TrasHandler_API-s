from kafka import KafkaProducer
import json
producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
def send_location_update(action, data, vendor_id):
    data_with_action = {
        'action': action,
        'vendor_id': vendor_id,
        'data': data
    }

    # Log the data being sent
    print(f"Sending to Kafka: {json.dumps(data_with_action, indent=4)}")

    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send('vendor-location-topic', value=data_with_action)
    producer.flush()
