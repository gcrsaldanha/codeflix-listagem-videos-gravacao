from abc import ABC

from src.domain.category import Category
from src.domain.repository import Repository


class CategoryRepository(Repository[Category], ABC):
    pass
