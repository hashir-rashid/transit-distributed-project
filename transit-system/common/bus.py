import logging
import os
import time

import pika

EXCHANGE = "transit"          # the name of our "post office" in RabbitMQ
log = logging.getLogger("bus")


class MessageBus:
    def __init__(self):
        # In Docker the host is "rabbitmq"; on your laptop it's "localhost"
        host = os.getenv("RABBITMQ_HOST", "localhost")
        self.connection = self._connect(host)
        self.channel = self.connection.channel()
        # "topic" exchange = route messages by their address, e.g. "vehicle.location"
        self.channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    def _connect(self, host):
        # Keep retrying: RabbitMQ can take a few seconds to start
        for attempt in range(30):
            try:
                return pika.BlockingConnection(pika.ConnectionParameters(host=host))
            except pika.exceptions.AMQPConnectionError:
                log.warning("RabbitMQ not ready, retrying in 2s...")
                time.sleep(2)
        raise RuntimeError("Could not connect to RabbitMQ")

    def publish(self, routing_key, message):
        """Send a message (any class from common.messages) to an address."""
        self.channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=routing_key,
            body=message.to_json(),
        )

    def subscribe(self, routing_keys, callback):
        """Listen for messages on the given addresses. Runs forever.
        callback(routing_key, body) is called for each message.
        Use ["#"] to receive every message."""
        queue = self.channel.queue_declare(queue="", exclusive=True).method.queue
        for key in routing_keys:
            self.channel.queue_bind(exchange=EXCHANGE, queue=queue, routing_key=key)

        def on_message(ch, method, properties, body):
            callback(method.routing_key, body)

        self.channel.basic_consume(queue=queue, on_message_callback=on_message, auto_ack=True)
        self.channel.start_consuming()

    def sleep(self, seconds):
        """Use this instead of time.sleep() so the connection stays alive."""
        self.connection.sleep(seconds)