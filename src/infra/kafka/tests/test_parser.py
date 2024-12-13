from pytest_mock import MockFixture

from src.infra.kafka.consumer import Category
from src.infra.kafka.parser import ParsedEvent, parse_debezium_message
from src.infra.kafka.operation import Operation


class TestParseDebeziumMessage:
    def test_parse_created_message(self):
        data = b'{"payload": {"source": {"table": "categories"}, "op": "c", "after": {"id": 1, "external_id": "d5889ed5-3d3f-11ef-baf5-0242ac130006", "name": "Category 1", "description": "Description 1", "created_at": "2022-01-01", "updated_at": "2022-01-01", "is_active": true}}}'
        parsed_event = parse_debezium_message(data)
        expected_event = ParsedEvent(
            entity=Category,
            operation=Operation.CREATE,
            payload={
                "id": 1,
                "external_id": "d5889ed5-3d3f-11ef-baf5-0242ac130006",
                "name": "Category 1",
                "description": "Description 1",
                "created_at": "2022-01-01",
                "updated_at": "2022-01-01",
                "is_active": True,
            },
        )
        assert parsed_event == expected_event

    def test_parse_updated_message(self):
        data = b'{"payload": {"source": {"table": "categories"}, "op": "u", "before": {"id": 1, "external_id": "d5889ed5-3d3f-11ef-baf5-0242ac130006", "name": "Category 1", "description": "Description 1", "created_at": "2022-01-01", "updated_at": "2022-01-01", "is_active": true}, "after": {"id": 1, "external_id": "d5889ed5-3d3f-11ef-baf5-0242ac130006", "name": "Category 1 Updated", "description": "Description 1 Updated", "created_at": "2022-01-01", "updated_at": "2022-01-01", "is_active": true}}}'
        parsed_event = parse_debezium_message(data)
        expected_event = ParsedEvent(
            entity=Category,
            operation=Operation.UPDATE,
            payload={
                "id": 1,
                "external_id": "d5889ed5-3d3f-11ef-baf5-0242ac130006",
                "name": "Category 1 Updated",
                "description": "Description 1 Updated",
                "created_at": "2022-01-01",
                "updated_at": "2022-01-01",
                "is_active": True,
            },
        )
        assert parsed_event == expected_event

    def test_parse_deleted_message(self):
        data = b'{"payload": {"source": {"table": "categories"}, "op": "d", "before": {"id": 1, "external_id": "d5889ed5-3d3f-11ef-baf5-0242ac130006", "name": "Category 1", "description": "Description 1", "created_at": "2022-01-01", "updated_at": "2022-01-01", "is_active": true}, "after": null }}'
        parsed_event = parse_debezium_message(data)
        expected_event = ParsedEvent(
            entity=Category,
            operation=Operation.DELETE,
            payload={
                "id": 1,
                "external_id": "d5889ed5-3d3f-11ef-baf5-0242ac130006",
                "name": "Category 1",
                "description": "Description 1",
                "created_at": "2022-01-01",
                "updated_at": "2022-01-01",
                "is_active": True,
            },
        )
        assert parsed_event == expected_event

    def test_when_message_is_invalid_json_then_return_none_and_log_error(self, mocker: MockFixture):
        log_error = mocker.patch("src.infra.kafka.parser.logger.error")
        data = b'{"payload": {"source": {"table": "categories"}, "op": "c", "after": {"id": 1, "external_id": "d5889ed5-3d3f-11ef-baf5-0242ac130006", "name": "Category 1", "description": "Description 1", "created_at": "2022-01-01", "updated_at": "2022-01-01", "is_active": true}'
        parsed_event = parse_debezium_message(data)
        assert parsed_event is None
        log_error.assert_called_once()

    def test_when_message_is_missing_required_key_then_return_none(self, mocker: MockFixture):
        log_error = mocker.patch("src.infra.kafka.parser.logger.error")
        data = b'{"payload": {}}'
        parsed_event = parse_debezium_message(data)
        assert parsed_event is None
        log_error.assert_called_once()
