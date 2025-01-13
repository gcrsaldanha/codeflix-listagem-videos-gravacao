from unittest.mock import create_autospec

from src.domain.category import Category
from src.infra.kafka.abstract_event_handler import AbstractEventHandler
from src.infra.kafka.operation import Operation
from src.infra.kafka.parser import ParsedEvent


class FakeHandler(AbstractEventHandler):
    def handle_updated(self, event: ParsedEvent) -> None:
        pass

    def handle_deleted(self, event: ParsedEvent) -> None:
        pass

    def handle_created(self, event: ParsedEvent) -> None:
        pass


class TestAbstractEventHandler:
    def test_when_operation_is_create_then_call_handle_created(self):
        event = ParsedEvent(
            entity=Category,
            operation=Operation.CREATE,
            payload={"key": "value"},
        )
        handler = FakeHandler()
        handler.handle_created = create_autospec(handler.handle_created)
        handler(event)

        handler.handle_created.assert_called_once_with(event)

    def test_when_operation_is_update_then_call_handle_updated(self):
        event = ParsedEvent(
            entity=Category,
            operation=Operation.UPDATE,
            payload={"key": "value"},
        )
        handler = FakeHandler()
        handler.handle_updated = create_autospec(handler.handle_updated)
        handler(event)

        handler.handle_updated.assert_called_once_with(event)

    def test_when_operation_is_delete_then_call_handle_deleted(self):
        event = ParsedEvent(
            entity=Category,
            operation=Operation.DELETE,
            payload={"key": "value"},
        )
        handler = FakeHandler()
        handler.handle_deleted = create_autospec(handler.handle_deleted)
        handler(event)

        handler.handle_deleted.assert_called_once_with(event)

    def test_when_operation_is_unknown_then_log_info(self, mocker):
        event = ParsedEvent(
            entity=Category,
            operation="unknown",  # type: ignore
            payload={"key": "value"},
        )
        handler = FakeHandler()
        logger = mocker.patch("src.infra.kafka.abstract_event_handler.logger")
        handler(event)

        logger.info.assert_called_once_with(f"Unknown operation: {event.operation}")
