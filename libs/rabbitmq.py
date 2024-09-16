import pika
import json


class RabbitMQ:
    def __init__(self, host="localhost", queue_name="recognize"):
        self.host = host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)

    def close(self):
        if self.connection:
            self.connection.close()

    def publish(self, message):
        if not self.channel:
            self.connect()
        self.channel.basic_publish(
            exchange="", routing_key=self.queue_name, body=json.dumps(message)
        )

    def consume(self, callback):
        if not self.channel:
            self.connect()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=callback, auto_ack=False
        )
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()

    def acknowledge(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)
