# Módulo 5 - Elasticsearch Category Repository

# Aula 5.1 - Integrando nossa aplicação com Elasticsearch

Já temos o `CategoryRepository` e agora precisamos da nossa implementação desse repositório integrada com o
Elasticsearch.

Lembrando que esse **não é um curso** de Elasticsearch. Já temos cursos com esse foco aqui na plataforma. Então não vou
ficar passando em detalhes as configurações e se você quiser se aprofundar, recomendo ler a documentação oficial.

* Instalar `elasticsearch==8.13.2`
* Criar `ElasticsearchCategoryRepository` implementando `CategoryRepository`
    * [elasticsearch_category_repository.py](../src/infra/elasticsearch/elasticsearch_category_repository.py)
* Passar o cliente `Elasticsearch` por dependência
* Implementar `search` simples (sem filtros)
* Exibir http://localhost:9200/catalog-db.codeflix.categories/_search para entendermos o que estamos parseando.
* Lidar com instâncias *malformed* (`try/except ValidationError`)
* Executar o `search()` via shell.

```python
from src.infra.elasticsearch.elasticsearch_category_repository import ElasticsearchCategoryRepository

repo = ElasticsearchCategoryRepository()
print(repo.search())
```

# Aula 5.2 - Testando ElasticsearchCategoryRepository

Para testar a implementação do nosso repository, vamos precisar de uma instância de testes do Elasticsearch.

Vamos criar um novo service no nosso `docker-compose.yml` para subir o Elasticsearch.

```yaml
  elasticsearch-test:
    container_name: elasticsearch-test
    hostname: elasticsearch-test
    image: docker.elastic.co/elasticsearch/elasticsearch:8.13.4
    ports:
      - "9201:9200"  # Vamos usar a porta 9201 no host
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms128m -Xmx128m"  # Limitar memória para 128MB, evitar exit code 137. Atualizar elastisearch.
      - "indices.fielddata.cache.size=5%"
    profiles:
      - test  # Para garantir que `docker compose up` não suba o container de testes automaticamente.
```

Criar `test_elasticsearch_category_repository.py`: [test_elasticsearch_category_repository.py](../src/test_elasticsearch_category_repository.py)

Vamos criar um teste para garantir que o repositório consegue se comunicar com a instância do Elasticsearch.

```python
  def test_can_reach_elasticsearch_test_database() -> None:
    es = Elasticsearch(hosts=[ELASTICSEARCH_HOST_TEST])

    assert es.ping()
```

Vai falhar, pois precisamos garantir que o Elasticsearch esteja rodando antes de rodar os testes.

```bash
docker compose up -d elasticsearch-test
```

Queremos escrever alguns casos de teste:

* test_can_reach_elasticsearch_test_database
* test_when_index_is_empty_then_return_empty_list
* test_when_index_has_categories_then_return_mapped_categories_with_default_search
* test_when_index_has_malformed_categories_then_return_valid_categories_and_log_error

Vamos precisar de uma fixture para criar o índice no Elasticsearch antes de rodar os testes e deletar o índice depois.

```python
class TestSearch:
    @pytest.fixture
    def es(self) -> Elasticsearch:
        es = Elasticsearch(hosts=[ELASTICSEARCH_HOST_TEST])
        if not es.indices.exists(index=CATEGORY_INDEX):
            es.indices.create(index=CATEGORY_INDEX)

        yield es
        es.indices.delete(index=CATEGORY_INDEX)

```

E também vamos precisar de fixtures para categorias, podemos copiar as que utilizamos anteriormente: `movie_category`
e `series_category`.

Como indexar um documento:

```python
es.index(
    index=CATEGORY_INDEX,
    id=str(series_category.id),
    body=series_category.model_dump(mode="json"),
    refresh=True,
)

```

> Ao indexar um documento, passamos `refresh=True` para garantir que o documento vai estar disponível para busca
> imediatamente.

Terminar de escrever os testes e passar o `client` e `logger` como dependência para o `ElasticsearchCategoryRepository`.

# Aula 5.3 - Ordenação (sorting)

Para evitar inconsistências, vamos fazer um cleanup do nosso MySQL e do Elasticsearch.

```bash
curl -X DELETE "http://localhost:9200/catalog-db.codeflix.categories"
```

```mysql
DELETE
FROM category
where true;
```

Agora vamos escrever os nossos testes:

* test_when_no_sorting_is_specified_then_return_categories_ordered_by_insertion_order
* test_return_categories_ordered_by_name_asc
* test_return_categories_ordered_by_name_desc

Para deixar mais explícito o comportamento, vamos criar uma nova fixture para `documentary_category`.

Small refactor: ao invés de `CATEGORY_INDEX`, mover para uma constante `INDEX`.

```python
class ElasticsearchCategoryRepository:
    INDEX = "catalog-db.codeflix.categories"
    ...
```

Implementação do repositório:

```python
query = {
    "sort": [{f"{sort}.keyword": {"order": direction}}] if sort else [],  # Use .keyword for exact match
}

response = self._client.search(
    index=self.INDEX,
    body=query,
)
```

> .keyword garante que vamos ordenar exatamente pelo valor completo do campo (exact match), sem aplicar nenhum tipo de
> análise. Caso contrário, poderíamos ter resultados inesperados com campos com mais de 1 palavra.

# Aula 5.4 - Paginação (pagination)

Vamos escrever os seguintes testes:

* test_when_no_page_is_requested_then_return_default_paginated_response
* test_when_page_is_requested_then_return_expected_paginated_response
* test_when_requested_page_is_out_of_bounds_then_return_empty_list

Para facilitar, vamos criar uma fixture já populando o Elasticsearch com categorias:

```python
    @pytest.fixture
def populated_es(
        self,
        es: Elasticsearch,
        movie_category: Category,
        series_category: Category,
        documentary_category: Category,
) -> Elasticsearch:
    es.index(
        index=ElasticsearchCategoryRepository.INDEX,
        id=str(movie_category.id),
        body=movie_category.model_dump(mode="json"),
        refresh=True,
    )
    ...  # Indexar as outras categorias

    return es
```

E a implementação é bem simples:

```python
query = {
    "sort": [{f"{sort}.keyword": {"order": direction}}] if sort else [],  # Use .keyword for exact match
    "from": (page - 1) * per_page,
    "size": per_page,
}
```


# Aula 5.5 - Busca (search)

Agora vamos implementar a busca, que é a principal capacidade do Elasticsearch. Nós podemos especificar quais são os campos que queremos que sejam analisados para a busac. No nosso caso, utilizaremos `name` e `description`.

A sintaxe é um pouquinho mais complexa:
```python
        query = {
            "from": (page - 1) * per_page,
            "size": per_page,
            "sort": [{f"{sort}.keyword": {"order": direction}}] if sort else [],
            "query": {
                "bool": {
                    "must": (
                        [{"multi_match": {"query": search, "fields": ["name", "description"]}}]
                        if search
                        else [{"match_all": {}}]
                    )
                }
            },
        }
```

E vamos adicionar alguns testes ao `TestSearch`:

* test_when_search_term_matches_category_name_then_return_matching_entities
* test_search_term_matches_both_name_and_description 
* test_search_is_case_insensitive
* test_search_by_non_existent_term_then_return_empty_list

> Refatorar TestSearch para utilizar `populated_es` onde fizer sentido


# Aula 5.6 - Teste de integração UseCase - Repository

Vamos criar um teste de integração para garantir que o `ListCategory` consegue utilizar o `ElasticsearchCategoryRepository` corretamente.

- [test_list_category.py](../src/tests/integration_tests/test_list_category.py)

Test cases:
- `test_list_categories_with_default_values`
- `test_list_categories_with_pagination_sorting_and_search`

Criamos uma pasta `unit_tests` e uma `integration_tests` para diferenciar testes que precisam de infraestrutura rodando (e.g.: Elasticsearch).

É perceptível que devido à baixa complexidade de regras de negócio da nossa aplicação, os testes de integração são os que fornecem o maior retorno para a gente.
