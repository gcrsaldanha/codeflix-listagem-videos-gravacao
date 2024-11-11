# Módulo 5 - Elasticsearch Category Repository

# Aula 5.1 - Integrando nossa aplicação com Elasticsearch

Já temos o `CategoryRepository` e agora precisamos da nossa implementação desse repositório integrada com o Elasticsearch.

Lembrando que esse **não é um curso** de Elasticsearch. Já temos cursos com esse foco aqui na plataforma. Então não vou ficar passando em detalhes as configurações e se você quiser se aprofundar, recomendo ler a documentação oficial.

* Instalar `elasticsearch==8.13.2`
* Criar `ElasticsearchCategoryRepository` implementando `CategoryRepository`
    * [elasticsearch_category_repository.py](../src/elasticsearch_category_repository.py)
* Passar o cliente `Elasticsearch` por dependência
* Implementar `search` simples (sem filtros)
* Exibir http://localhost:9200/catalog-db.codeflix.categories/_search para entendermos o que estamos parseando.
* Lidar com instâncias *malformed* (`try/except ValidationError`)
* Executar o `search()` via shell.

```python
from src.elasticsearch_category_repository import ElasticsearchCategoryRepository
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

E também vamos precisar de fixtures para categorias, podemos copiar as que utilizamos anteriormente: `movie_category` e `series_category`.

Como indexar um documento:
```python
es.index(
    index=CATEGORY_INDEX,
    id=str(series_category.id),
    body=series_category.model_dump(mode="json"),
    refresh=True,
)

```

> Ao indexar um documento, passamos `refresh=True` para garantir que o documento vai estar disponível para busca imediatamente.

Terminar de escrever os testes e passar o `client` e `logger` como dependência para o `ElasticsearchCategoryRepository`.
