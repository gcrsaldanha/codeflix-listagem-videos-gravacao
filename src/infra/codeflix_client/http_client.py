from uuid import UUID

from src.infra.codeflix_client.codeflix_client import CodeflixClient
from src.infra.codeflix_client.dtos import VideoResponse


class HttpClient(CodeflixClient):
    def get_video(self, id: UUID) -> VideoResponse:
        return VideoResponse(**{
            "id": id,
            "title": "The Godfather",
            "launch_year": 1972,
            "rating": "AGE_18",
            "is_active": True,
            "categories": [
                {
                    "id": "142f2b4b-1b7b-4f3b-8eab-3f2f2b4b1b7b",
                    "name": "Action",
                    "description": "Action movies",
                }
            ],
            "cast_members": [
                {
                    "id": "242f2b4b-1b7b-4f3b-8eab-3f2f2b4b1b7b",
                    "name": "Marlon Brando",
                    "type": "ACTOR",
                },
                {
                    "id": "342f2b4b-1b7b-4f3b-8eab-3f2f2b4b1b7b",
                    "name": "Al Pacino",
                    "type": "DIRECTOR",
                },
            ],
            "genres": [
                {
                    "id": "442f2b4b-1b7b-4f3b-8eab-3f2f2b4b1b7b",
                    "name": "Drama",
                }
            ],
            "banner": {
                "name": "The Godfather",
                "raw_location": "https://banner.com/the-godfather",
            },
        })
