from src.domain.entity import Entity


class Category(Entity):
    name: str
    description: str = ""
