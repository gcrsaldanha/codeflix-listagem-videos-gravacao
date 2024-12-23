import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig

from src.application.list_cast_member import CastMemberSortableFields, ListCastMember, ListCastMemberInput
from src.application.list_category import (
    CategorySortableFields,
    ListCategory,
    ListCategoryInput,
)
from src.application.listing import DEFAULT_PAGINATION_SIZE, SortDirection, ListOutputMeta
from src.domain.cast_member import CastMember
from src.domain.category import Category
from src.infra.api.http.dependencies import get_category_repository
from src.infra.elasticsearch.elasticsearch_cast_member_repository import ElasticsearchCastMemberRepository


@strawberry.experimental.pydantic.type(model=Category)
class CategoryGraphQL:
    id: strawberry.auto
    name: strawberry.auto
    description: strawberry.auto


@strawberry.experimental.pydantic.type(model=CastMember)
class CastMemberGraphQL:
    id: strawberry.auto
    name: strawberry.auto
    type: strawberry.auto


@strawberry.experimental.pydantic.type(model=ListOutputMeta, all_fields=True)
class Meta:
    pass


@strawberry.type
class Result[T]:
    data: list[T]
    meta: Meta


def get_categories(
    sort: CategorySortableFields = CategorySortableFields.NAME,
    search: str | None = None,
    page: int = 1,
    per_page: int = DEFAULT_PAGINATION_SIZE,
    direction: SortDirection = SortDirection.ASC,
) -> Result[CategoryGraphQL]:
    _repository = get_category_repository()
    use_case = ListCategory(repository=_repository)
    output = use_case.execute(
        ListCategoryInput(
            search=search,
            page=page,
            per_page=per_page,
            sort=sort,
            direction=direction,
        )
    )

    return Result(data=[
        CategoryGraphQL.from_pydantic(category) for category in output.data],
        meta=Meta.from_pydantic(output.meta),
    )


def get_cast_members(
    sort: CastMemberSortableFields = CastMemberSortableFields.NAME,
    search: str | None = None,
    page: int = 1,
    per_page: int = DEFAULT_PAGINATION_SIZE,
    direction: SortDirection = SortDirection.ASC,
) -> Result[CastMemberGraphQL]:
    repository = ElasticsearchCastMemberRepository()
    use_case = ListCastMember(repository=repository)
    output = use_case.execute(
        ListCastMemberInput(
            search=search,
            page=page,
            per_page=per_page,
            sort=sort,
            direction=direction,
        )
    )

    return Result(
        data=[CastMemberGraphQL.from_pydantic(cast_member) for cast_member in output.data],
        meta=Meta.from_pydantic(output.meta),
    )


@strawberry.type
class Query:
    categories: Result[CategoryGraphQL] = strawberry.field(resolver=get_categories)
    cast_members: Result[CastMemberGraphQL] = strawberry.field(resolver=get_cast_members)


schema = strawberry.Schema(query=Query, config=StrawberryConfig(auto_camel_case=False))
graphql_app = GraphQLRouter(schema)

# strawberry server src.infra.api.graphql.schema_pydantic --port 8001
