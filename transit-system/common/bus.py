import logging
import os
import time
from pathlib import Path

import pika

EXCHANGE = "transit"
log = logging.getLogger("bus")


def load_env_file():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


load_env_file()


class MessageBus:
    def __init__(self):
        host = os.getenv("RABBITMQ_HOST", "localhost")
        user = os.getenv("RABBITMQ_USER", "guest")
        password = os.getenv("RABBITMQ_PASSWORD", "guest")
        credentials = pika.PlainCredentials(user, password)

        self.connection = self._connect(host, credentials)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    def _connect(self, host, credentials):
        params = pika.ConnectionParameters(host=host, credentials=credentials)
        for attempt in range(30):
            try:
                return pika.BlockingConnection(params)
            except (pika.exceptions.ProbableAuthenticationError,
                    pika.exceptions.AuthenticationError):
                raise RuntimeError("RabbitMQ rejected the login: check RABBITMQ_USER and "
                                   "RABBITMQ_PASSWORD in your .env file")
            except pika.exceptions.AMQPConnectionError:
                log.warning("RabbitMQ not ready, retrying in 2s...")
                time.sleep(2)
        raise RuntimeError("Could not connect to RabbitMQ")

    def publish(self, routing_key, message):
        self.channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=routing_key,
            body=message.to_json(),
        )

    def subscribe(self, routing_keys, callback):

        queue = self.channel.queue_declare(queue="", exclusive=True).method.queue
        for key in routing_keys:
            self.channel.queue_bind(exchange=EXCHANGE, queue=queue, routing_key=key)

        def on_message(ch, method, properties, body):
            callback(method.routing_key, body)

        self.channel.basic_consume(queue=queue, on_message_callback=on_message, auto_ack=True)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Stopped listening.")
            self.connection.close()

    def sleep(self, seconds):
        self.connection.sleep(seconds)