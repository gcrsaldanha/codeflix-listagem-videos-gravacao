import logging
import os
from typing import Callable, Type

from confluent_kafka import KafkaException, Consumer as KafkaConsumer

from src.domain.entity import Entity
from src.domain.video import Video
from src.infra.kafka.abstract_event_handler import AbstractEventHandler
from src.infra.kafka.parser import ParsedEvent, parse_debezium_message
from src.infra.kafka.video_event_handler import VideoEventHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("consumer")

# Configuration for the Kafka consumer
config = {
    "bootstrap.servers": os.getenv("BOOTSTRAP_SERVERS", "kafka:19092"),
    "group.id": "consumer-cluster",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
}
topics = [
    "catalog-db.codeflix.videos",
]

# Similar to a "router" -> calls proper handler
entity_to_handler: dict[Type[Entity], Type[AbstractEventHandler]] = {
    # Category: CategoryEventHandler,
    # CastMember: CastMemberEventHandler,
    # Genre: GenreEventHandler,
    Video: VideoEventHandler,
}


class Consumer:
    def __init__(
        self,
        client: KafkaConsumer,
        parser: Callable[[bytes], ParsedEvent | None],
        router: dict[Type[Entity], Type[AbstractEventHandler]] | None = None,
    ) -> None:
        """
        :param client: Kafka consumer client
        :param parser: Function to parse the message data to a ParsedEvent
        :param router:  Dictionary to route the event to the proper handler
        """
        self.client = client
        self.parser = parser
        self.router = router or entity_to_handler

    def start(self):
        logger.info("Starting consumer...")
        try:
            while True:
                self.consume()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
        except KafkaException as e:
            logger.error(e)
        finally:
            self.stop()

    def consume(self) -> None:
        message = self.client.poll(timeout=1.0)
        if message is None:
            logger.info("No message received")
            return None

        if message.error():
            logger.error(f"received message with error: {message.error()}")
            return None

        message_data = message.value()
        if not message_data:
            logger.info("Empty message received")
            return None

        logger.info(f"Received message with data: {message_data}")
        parsed_event = self.parser(message_data)
        if parsed_event is None:
            logger.error(f"Failed to parse message data: {message_data}")
            return

        # Call the proper handler
        handler = self.router[parsed_event.entity]()
        handler(parsed_event)

        self.client.commit(message=message)

    def stop(self):
        logger.info("Closing consumer...")
        self.client.close()


if __name__ == "__main__":
    kafka_consumer = KafkaConsumer(config)
    kafka_consumer.subscribe(topics=topics)
    consumer = Consumer(client=kafka_consumer, parser=parse_debezium_message)
    consumer.start()
