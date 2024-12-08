from elasticsearch import Elasticsearch

from src.application.list_genre import ListGenre, GenreSortableFields, ListGenreInput
from src.application.listing import ListOutputMeta
from src.domain.category import Category
from src.domain.genre import Genre
from src.domain.repository import SortDirection
from src.infra.elasticsearch.elasticsearch_genre_repository import ElasticsearchGenreRepository


class TestListGenre:
    def test_list_genre_with_default_values_and_nested_categories_ids(
        self,
        populated_es: Elasticsearch,
        movie: Category,
        documentary: Category,
        drama: Genre,
        romance: Genre,
    ) -> None:
        output = ListGenre(
            repository=ElasticsearchGenreRepository(client=populated_es)
        ).execute(
            input=ListGenreInput()
        )

        assert output.data == [drama, romance]
        assert output.data[0].categories == {movie.id, documentary.id}
        assert output.data[1].categories == set()

        assert output.meta == ListOutputMeta(
            page=1,
            per_page=5,
            sort=GenreSortableFields.NAME,
            direction=SortDirection.ASC,
        )
