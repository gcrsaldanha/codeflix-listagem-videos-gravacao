import uuid
from unittest.mock import create_autospec

import pytest

from src.application.category.save_category import SaveCategory
from src.domain.category.category import Category
from src.infra.kafka.video_event_handler import CategoryEventHandler
from src.infra.kafka.parser import ParsedEvent
from src.infra.kafka.operation import Operation


class TestHandleCreated:
    def test_call_save_category_use_case(self):
        payload_uuid = uuid.uuid4()
        event = ParsedEvent(
            entity=Category,
            operation=Operation.CREATE,
            payload={
                "external_id": payload_uuid,
                "name": "name",
                "description": "description",
                "created_at": "2021-08-21T00:00:00",
                "updated_at": "2021-08-21T00:00:00",
                "is_active": True,
            },
        )

        save_category_use_case = create_autospec(SaveCategory)
        handler = CategoryEventHandler(save_use_case=save_category_use_case)

        handler.handle_created(event)

        expected_input = SaveCategory.Input(
            category=Category(
                id=payload_uuid,
                name="name",
                description="description",
                created_at="2021-08-21T00:00:00",
                updated_at="2021-08-21T00:00:00",
                is_active=True,
            )
        )
        save_category_use_case.execute.assert_called_once_with(input=expected_input)


class TestHandleUpdated:
    def test_call_save_category_use_case(self):
        payload_uuid = uuid.uuid4()
        event = ParsedEvent(
            entity=Category,
            operation=Operation.UPDATE,
            payload={
                "external_id": payload_uuid,
                "name": "name",
                "description": "description",
                "created_at": "2021-08-21T00:00:00",
                "updated_at": "2021-08-21T00:00:00",
                "is_active": True,
            },
        )

        save_category_use_case = create_autospec(SaveCategory)
        handler = CategoryEventHandler(save_use_case=save_category_use_case)

        handler.handle_updated(event)

        expected_input = SaveCategory.Input(
            category=Category(
                id=payload_uuid,
                name="name",
                description="description",
                created_at="2021-08-21T00:00:00",
                updated_at="2021-08-21T00:00:00",
                is_active=True,
            )
        )
        save_category_use_case.execute.assert_called_once_with(input=expected_input)
