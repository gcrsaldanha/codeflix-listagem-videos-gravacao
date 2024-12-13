from unittest.mock import create_autospec, MagicMock

import pytest
from pytest_mock import MockFixture
from confluent_kafka import KafkaException, Consumer as KafkaConsumer, Message

from src.domain.category.category import Category
from src.infra.kafka.consumer import Consumer

# from src.infra.kafka.abstract_kafka_client import AbstractKafkaClient
from src.infra.kafka.parser import parse_debezium_message


@pytest.fixture
def consumer() -> Consumer:
    client = create_autospec(KafkaConsumer)
    return Consumer(client=client, parser=parse_debezium_message)


@pytest.fixture
def error_message() -> Message:
    message = create_autospec(Message)
    message.error.return_value = "error"
    return message


@pytest.fixture
def empty_message() -> Message:
    message = create_autospec(Message)
    message.error.return_value = None
    message.value.return_value = None
    return message


@pytest.fixture
def message_with_invalid_data() -> Message:
    message = create_autospec(Message)
    message.error.return_value = None
    message.value.return_value = b"not a json data"
    return message


@pytest.fixture
def message_with_create_data() -> Message:
    message = create_autospec(Message)
    message.error.return_value = None
    message.value.return_value = b'{"payload": {"source": {"table": "categories"}, "op": "c", "after": {"id": 1, "external_id": "d5889ed5-3d3f-11ef-baf5-0242ac130006", "name": "Category 1", "description": "Description 1", "created_at": "2022-01-01", "updated_at": "2022-01-01", "is_active": true}}}'
    return message


@pytest.fixture
def consumer_logger(mocker: MockFixture) -> MagicMock:
    return mocker.patch("src.infra.kafka.consumer.logger")


class TestConsume:
    def test_when_no_message_is_available_in_poll_then_return_none(
        self,
        consumer: Consumer,
    ) -> None:
        consumer.client.poll.return_value = None

        assert consumer.consume() is None

    def test_when_message_has_error_then_log_error_and_return_none(
        self,
        consumer: Consumer,
        error_message: Message,
        consumer_logger: MagicMock,
    ) -> None:
        consumer.client.poll.return_value = error_message

        assert consumer.consume() is None
        consumer_logger.error.assert_called_once_with("received message with error: error")

    def test_when_message_data_is_empty_then_return_none(
        self,
        consumer: Consumer,
        empty_message: Message,
        consumer_logger: MagicMock,
    ) -> None:
        consumer.client.poll.return_value = empty_message

        assert consumer.consume() is None
        consumer_logger.assert_not_called()

    def test_when_cannot_parse_message_data_then_log_error_and_return_none(
        self,
        consumer: Consumer,
        message_with_invalid_data: Message,
        consumer_logger: MagicMock,
    ) -> None:
        consumer.client.poll.return_value = message_with_invalid_data

        assert consumer.consume() is None
        consumer_logger.info.assert_called_once_with("Received message with data: b'not a json data'")
        consumer_logger.error.assert_called_once_with("Failed to parse message data: b'not a json data'")

    def test_when_message_data_is_valid_then_parse_and_call_handler(
        self,
        consumer: Consumer,
        message_with_create_data: Message,
        mocker: MockFixture,
    ) -> None:
        consumer.client.poll.return_value = message_with_create_data
        mock_handler = mocker.MagicMock()
        consumer.router = {Category: mock_handler}

        consumer.consume()

        mock_handler.assert_called_once()

        consumer.client.commit.assert_called_once_with(message=message_with_create_data)


class TestStart:
    def test_consume_message_until_keyboard_interruption(
        self,
        consumer: Consumer,
        mocker: MockFixture,
    ) -> None:
        consumer.consume = mocker.MagicMock(side_effect=[None, KeyboardInterrupt])
        consumer.start()

        assert consumer.consume.call_count == 2
        consumer.client.close.assert_called_once()

    def test_consume_message_until_kafka_exception(
        self,
        consumer: Consumer,
        mocker: MockFixture,
    ) -> None:
        consumer.consume = mocker.MagicMock(side_effect=[None, KafkaException("error")])
        consumer.start()

        assert consumer.consume.call_count == 2
        consumer.client.close.assert_called_once()
