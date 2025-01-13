import logging
from abc import ABC, abstractmethod

from src.infra.kafka.parser import ParsedEvent
from src.infra.kafka.operation import Operation

logger = logging.getLogger(__name__)


class AbstractEventHandler(ABC):
    @abstractmethod
    def handle_created(self, event: ParsedEvent) -> None:
        pass

    @abstractmethod
    def handle_updated(self, event: ParsedEvent) -> None:
        pass

    @abstractmethod
    def handle_deleted(self, event: ParsedEvent) -> None:
        pass

    def __call__(self, event: ParsedEvent) -> None:
        if event.operation == Operation.CREATE:
            self.handle_created(event)
        elif event.operation == Operation.UPDATE:
            self.handle_updated(event)
        elif event.operation == Operation.DELETE:
            self.handle_deleted(event)
        else:
            logger.info(f"Unknown operation: {event.operation}")
