import pika
import os
import json
import logging

logger = logging.getLogger(__name__)

def get_rabbitmq_connection():
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")
    parameters = pika.URLParameters(url)
    return pika.BlockingConnection(parameters)

class EventPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = get_rabbitmq_connection()
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange='maestro_events', exchange_type='topic')

    def publish(self, topic: str, message: dict):
        self.connect()
        self.channel.basic_publish(
            exchange='maestro_events',
            routing_key=topic,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        logger.info(f"Published event to {topic}")

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

class EventConsumer:
    def __init__(self, queue_name: str, topic_pattern: str):
        self.queue_name = queue_name
        self.topic_pattern = topic_pattern
        self.connection = None
        self.channel = None

    def connect(self):
        self.connection = get_rabbitmq_connection()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='maestro_events', exchange_type='topic')
        
        result = self.channel.queue_declare(queue=self.queue_name, durable=True)
        self.channel.queue_bind(
            exchange='maestro_events',
            queue=self.queue_name,
            routing_key=self.topic_pattern
        )

    def consume(self, callback):
        self.connect()
        def on_message(ch, method, properties, body):
            data = json.loads(body)
            callback(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=on_message)
        logger.info(f"Started consuming on {self.queue_name} for topics {self.topic_pattern}")
        self.channel.start_consuming()

publisher = EventPublisher()
