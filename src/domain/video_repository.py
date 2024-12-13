from abc import ABC, abstractmethod

from src.domain.repository import Repository
from src.domain.video import Video


class VideoRepository(Repository[Video], ABC):
    @abstractmethod
    def save(self, video: Video) -> None:
        raise NotImplementedError
