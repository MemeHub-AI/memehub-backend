import pika
from pika.adapters.blocking_connection import BlockingChannel
from django.conf import settings

__all__ = ["RabbitServer", "consume_by_rabbit"]


class RabbitServer:
    def __init__(self, channel_number, topic, user="producer"):
        self.channel_number = channel_number
        self.topic = topic
        self.params = pika.ConnectionParameters(
            settings.RABBIT_HOST,
            port=settings.RABBIT_PORT,
            credentials=pika.credentials.PlainCredentials(user, settings.RABBIT_SECRET),
        )

        self.channel = self.get_connection()
        self.channel.queue_declare(topic, durable=True)

    def publish(self, topic, value):
        for _ in range(3):
            try:
                channel.basic_publish(exchange="", routing_key=topic, body=value)
                break
            except:
                channel = self.get_connection()

    def get_connection(self):
        con = pika.BlockingConnection(self.params)
        return con.channel(self.channel_number)


def consume_by_rabbit(func, topic="meme_hub"):
    rabbit_client = RabbitServer(9, topic, "consumer").channel

    def rabbitmq_callback(channel, method, properties, body: bytes):
        func(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    rabbit_client.basic_qos(prefetch_count=1)
    rabbit_client.basic_consume(topic, on_message_callback=rabbitmq_callback)
    try:
        print("Start monitoring")
        rabbit_client.start_consuming()
    except (KeyboardInterrupt, SystemExit):
        print("System exit")
        rabbit_client.stop_consuming()
