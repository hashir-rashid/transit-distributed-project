import logging
import os
import time
from pathlib import Path

import pika

EXCHANGE = "transit"          # the name of our "post office" in RabbitMQ
log = logging.getLogger("bus")


def load_env_file():
    """Read KEY=VALUE lines from the .env file in the project root, if it exists.
    (In Docker, the values come from docker-compose instead.)"""
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
        # In Docker the host is "rabbitmq"; on your laptop it's "localhost"
        host = os.getenv("RABBITMQ_HOST", "localhost")
        # Log in with the username and password instead of the default guest account
        user = os.getenv("RABBITMQ_USER", "guest")
        password = os.getenv("RABBITMQ_PASSWORD", "guest")
        credentials = pika.PlainCredentials(user, password)

        self.connection = self._connect(host, credentials)
        self.channel = self.connection.channel()
        # "topic" exchange = route messages by their address, e.g. "vehicle.location"
        self.channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    def _connect(self, host, credentials):
        # Keep retrying: RabbitMQ can take a few seconds to start
        params = pika.ConnectionParameters(host=host, credentials=credentials)
        for attempt in range(30):
            try:
                return pika.BlockingConnection(params)
            except (pika.exceptions.ProbableAuthenticationError,
                    pika.exceptions.AuthenticationError):
                # Wrong username/password: retrying won't help, so stop with a clear message
                raise RuntimeError("RabbitMQ rejected the login: check RABBITMQ_USER and "
                                   "RABBITMQ_PASSWORD in your .env file")
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
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Stopped listening.")
            self.connection.close()

    def sleep(self, seconds):
        """Use this instead of time.sleep() so the connection stays alive."""
        self.connection.sleep(seconds)