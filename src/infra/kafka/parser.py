import json
import logging
from dataclasses import dataclass
from typing import Type

from src.domain.cast_member import CastMember
from src.domain.category import Category
from src.domain.entity import Entity
from src.domain.genre import Genre
from src.domain.video import Video
from src.infra.kafka.operation import Operation

logger = logging.getLogger(__name__)


@dataclass
class ParsedEvent:
    entity: Type[Entity]
    operation: Operation
    payload: dict


table_to_entity = {
    "categories": Category,
    "cast_members": CastMember,
    "genres": Genre,
    "videos": Video,
}


def parse_debezium_message(data: bytes) -> ParsedEvent | None:
    try:
        json_data = json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as e:
        logger.error(e)
        return None

    try:
        entity = table_to_entity[json_data["payload"]["source"]["table"]]
        operation = Operation(json_data["payload"]["op"])
        payload = json_data["payload"]["after"] if operation != Operation.DELETE else json_data["payload"]["before"]
    except (KeyError, ValueError) as e:
        logger.error(e)
        return None

    return ParsedEvent(entity=entity, operation=operation, payload=payload)
