# Módulo 11 - GraphQL

# Aula 11.1 - Definindo nosso GraphQL schema

- Instalar: [Strawberry GraphQL + FastAPI Docs](https://strawberry.rocks/docs/integrations/fastapi)

```bash
pip install 'strawberry-graphql[fastapi]'

# strawberry-graphql==0.254.0
```

- Apresentar o [schema](../src/infra/api/graphql/schema.graphql)
- Implementar o schema:

```python
@strawberry.type
class CategoryGraphQL:
    id: UUID
    name: str
    description: str = ""


@strawberry.type
class Meta:
    page: int = 1
    per_page: int = DEFAULT_PAGINATION_SIZE
    sort: str | None
    direction: SortDirection = SortDirection.ASC


@strawberry.type
class Result[T]:
    data: list[T]
    meta: Meta


def get_categories() -> Result[CategoryGraphQL]:
    return Result(
        data=[
            CategoryGraphQL(id=uuid4(), name="Category 1"),
            CategoryGraphQL(id=uuid4(), name="Category 2"),
        ]
    )


@strawberry.type
class Query:
    categories: Result[CategoryGraphQL] = strawberry.field(resolver=get_categories)


schema = strawberry.Schema(query=Query)
```

- Executar o servidor GraphQL:

```bash
strawberry server src.infra.api.graphql.schema --port 8001
```

- Fazer algumas consultas

# Aula 11.2 - Implementando o resolver get_categories

- Revisar [CleanArch](./resources/cleanArch.jpeg)
- Muito similar a uma "view" do FastAPI

```python
def get_categories() -> Result[CategoryGraphQL]:
    use_case = ListCategory(repository=ElasticsearchCategoryRepository())
    output = use_case.execute(ListCategoryInput())

    return Result(
        data=[CategoryGraphQL.from_pydantic(category) for category in output.data],
        meta=Meta.from_pydantic(output.meta),
    )
```

# Aula 11.3 - Passando argumentos para a API

```python
def get_categories(
        sort: CategorySortableFields = CategorySortableFields.NAME,
        search: str | None = None,
        page: int = 1,
        per_page: int = DEFAULT_PAGINATION_SIZE,
        direction: SortDirection = SortDirection.ASC,
) -> Result[CategoryGraphQL]:
    ...
    output = use_case.execute(
        ListCategoryInput(
            search=search,
            page=page,
            per_page=per_page,
            sort=sort,
            direction=direction,
        )
    )
    ...
```

# Aula 11.4 - Suporte ao Pydantic

> Documentação: https://strawberry.rocks/docs/integrations/pydantic
> 

```python
@strawberry.experimental.pydantic.type(model=Category)
class CategoryGraphQL:
    id: strawberry.auto
    name: strawberry.auto
    description: strawberry.auto


@strawberry.experimental.pydantic.type(model=ListOutputMeta, all_fields=True)
class Meta:
    pass


@strawberry.type
class Result[T]:
    data: list[T]
    meta: Meta


def get_categories(...) -> Result[CategoryGraphQL]:
    ...
    return Result(
        data=[CategoryGraphQL.from_pydantic(category) for category in output.data],
        meta=Meta.from_pydantic(output.meta),
    )

schema = strawberry.Schema(query=Query, config=StrawberryConfig(auto_camel_case=False))
```

> Remover auto camelCase: https://strawberry.rocks/docs/types/schema-configurations
 

# Aula 11.5 - Integrando com FastAPI

```python
# schema.py
graphql_app = GraphQLRouter(schema)

# main.py
app.include_router(graphql_router, prefix="/graphql")
```

Basta fazer requests para `http://localhost:8000/graphql` com o payload correto. Podemos copiar o request feito na interface do Strawberry.


# Aula 11.6 - Testando a API GraphQL

Como estamos expondo a API via FastAPI, podemos reutilizar o test client de `test_list_category_api.py`.

Basta executar um `post` na API correta com o payload do GraphQL.

Precisamos garantir que vamos utilizar o Elasticsearch de teste. Porém, Strawberry ainda não suporta injeção de dependência nos resolvers (similar ao `Depends` do FastAPI).
Portanto, podemos utilizar o `mock.patch` do Python e mockar o retorno de `get_category_repository`.

Atualizar o retorno esperado de acordo com GraphQL model - mais um exemplo da "camada" onde estamos atuando.

> Strawberry enum utiliza o name ao invés do value do enum. Precisamos ajustar isso também.


# Aula 11.7 - Adicionando CastMembers

Simplesmente duplicar o que fizemos para Category.


# Desafio: Genre e Video

Implementar a Query GraphQL para Genre e Video.
Opcional: refatorar o código extraindo os resolvers / schemas para arquivos separados.
