# Módulo 9 - Genre

# Aula 9.1 - Sink MySQL - Elasticsearch

Criar tabela `genres`, idêntica à `categories` mas apenas com o campo `name`. Vamos implementar o relacionamento
entre `categories` e `genres` depois.

```mysql
CREATE TABLE genres
(
    id         VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name       VARCHAR(255) NOT NULL,
    is_active  BOOLEAN                 DEFAULT TRUE,
    created_at TIMESTAMP               DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP               DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO genres (name)
VALUES ('Drama')
;

SELECT *
FROM genres;
```

Se o Kafka Connect estiver rodando com o Debezium configurado, um novo tópico será automaticamente criado:

```bash
make list-topics

...
>>> catalog-db.codeflix.genres
...
```

E se você realizou algumas inserções, pode verificar que os eventos foram enviados para o tópico corretamente:

```bash
make consume-topic topic=catalog-db.codeflix.genres
```

Agora basta atualizarmos o arquivo de [configuração do ElasticsearchSink](../kafka-connect/bin/elasticsearch-sink.json):

```
...
"topics": "catalog-db.codeflix.categories,catalog-db.codeflix.cast_members,catalog-db.codeflix.genres",
...
```

Remover o nosso elasticsearch connector e rodar o setup mais uma vez:

```bash
make delete-connector connector=elasticsearch
docker compose run --rm connect-setup
```

E verificar que os gêneros inseridos no banco de dados agora estão sincronizados no
Elasticsearch: http://localhost:9200/catalog-db.codeflix.genres/_search?

# Aula 9.2 - Domain Genre

- Referência do Catalog
  Admin: [Genre](https://github.com/gcrsaldanha/codeflix-catalog-admin/blob/main/src/core/genre/domain/genre.py)
    - `name` e `categories` (UUID)

Criar o domain `genre.py` herando de Entity.
Criar o `GenreRepository`.

# Aula 9.3 - Caso de uso ListGenre

Usar como referência o `ListCastMember` (mais atual).
Duplicar `list_cast_memer.py` e atualizar valores.

# Aula 9.4 - ElasticsearchGenreRepository pt.1

Criar o ElasticsearchGenreRepository sem as categories relacionadas.

Atualizar o `Genre(**hit["source"])` para um mais específico (já que o que vem do elasticsearch não é exatamente o que
queremos).

```python
parsed_entity = Genre(
    **hit["_source"],
    categories=set(),
)
```

# Aula 9.5 - API /genres

Copiar o cast_member_router.py.

Por enquanto o retorno vai ter sempre `categories` vazio.

# Aula 9.6 - Discussão sobre relacionamento entre gêneros e categorias

1. Fazer o Sink da tabela que relaciona gêneros e categorias e atualizar o ElasticsearchGenreRepository para trazer as
   categorias relacionadas.
2. Requisição HTTP para buscar as categorias associadas a um gênero no momento que um novo gênero é criado.
3. Utilizar Kafka Streams para criar um novo tópico com os gêneros e suas categorias já processados.
4. Utilizar ksqlDB para fazer o join entre os tópicos de gêneros e categorias e criar um novo tópico com os gêneros e
   suas categorias já processados.

Não tem "certo e errado", o importante é entender os tradeoffs e a arquitetura do sistema. No caso de (1), opção que
vamos seguir, nós assumimos um "sink total", armazenando as informações localmente.

Vantagem: simplicidade de código, mesma "infra" para todas entidades.
Desvantagem: uma consulta a mais para buscar as categorias associadas a um gênero (elasticsearch local)


> Mas a opção 2 também tem uma requisição EXTERNA a mais! Sim, mas ela ocorre apenas UMA vez, no momento do registro de
> um novo gênero.

Vamos seguir com a opção (1) por ser a mais simples. Se você quiser ver a opção utilizando Kafka Streams, recomendo que
assista às aulas do módulo de TypeScript.


# Aula 9.7 - Tabela genre_categories

Precisamos de uma tabela para relacionar um gênero às suas categorias:

```mysql
CREATE TABLE genre_categories
(
    id          VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),           -- precisamos do id por causa do nosso connector, senão teríamos que ter diferentes connectors
    genre_id    VARCHAR(36) NOT NULL,
    category_id VARCHAR(36) NOT NULL,
    FOREIGN KEY (genre_id) REFERENCES genres (id),
    FOREIGN KEY (category_id) REFERENCES categories (id),
    CONSTRAINT unique_genre_category UNIQUE (genre_id, category_id) -- Enforce uniqueness
);
```

Agora vamos adicionar o relacionamento entre o gênero "Drama" e as categorias "Filme" e "Documentário" (ou quaisquer
outras que você tenha criado):

```mysql
INSERT INTO genre_categories (genre_id, category_id)
SELECT g.id, c.id
FROM genres g
         JOIN categories c
WHERE g.name = 'Drama'
  AND c.name IN ('Filme', 'Documentario')
;
```

> Falar sobre caso não tivéssemos um `id` definido - bastaria definir outro connector para a composite key.

# Aula 9.8 - ElasticsearchGenreRepository pt.2

Agora que temos uma nova tabela relacionando gêneros e categorias, precisamos atualizar o `ElasticsearchGenreRepository`
para trazer as categorias relacionadas.

Antes, precisamos atualizar nosso Elasticsearch Sink Connector mais uma vez para incluir o tópico `genre_categories`:

Atualizar o arquivo de configuração `elasticsearch-sink.json`:

```
...
"topics": "catalog-db.codeflix.categories,catalog-db.codeflix.cast_members,catalog-db.codeflix.genres,catalog-db.codeflix.genre_categories",
...
```

Executar:

```bash
make delete-connector connector=elasticsearch
docker compose run --rm connect-setup
```

Confirmar que os dados estão sendo sincronizados no Elasticsearch:

```bash
curl -X GET "http://localhost:9200/catalog-db.codeflix.genre_categories/_search?pretty"
```

E atualizar onde `parsed_entity`:

```python
def fetch_categories_for_genre(self, genre_id: str) -> list[str]:
    query = {
        "query": {
            "term": {
                "genre_id.keyword": genre_id,
            },
        },
    }

    hits = self._client.search(index="catalog-db.codeflix.genre_categories", body=query)["hits"]["hits"]
    return [hit["_source"]["category_id"] for hit in hits]
```

# Aula 9.9 - Otimizando a busca de categorias

Atualmente temos o famoso problem N+1: onde para cada entidade `genre` fazemos uma nova requisição para buscar suas
categorias.

Vamos otimizar isso fazendo uma única requisição para buscar todas as categorias de todos os gêneros.

```python
...
genre_ids = [hit["_source"]["id"] for hit in hits]
categories_for_genres = self.fetch_categories_for_genres(genre_ids)
...
parsed_entity = Genre(
    **hit["_source"],
    categories=set(categories_for_genres.get(hit["_source"]["id"], [])),
)
...


def fetch_categories_for_genres(self, genre_ids: list[str]) -> dict[str, list[str]]:
    query = {
        "query": {
            "terms": {
                "genre_id.keyword": genre_ids,
            },
        },
    }

    hits = self._client.search(index=self._GENRE_CATEGORIES_INDEX, body=query)["hits"]["hits"]
    categories_by_genre = defaultdict(list)
    for hit in hits:
        categories_by_genre[hit["_source"]["genre_id"]].append(hit["_source"]["category_id"])

    return categories_by_genre
```

## Aula 9.10: UUID vs Objetos completos

Uma discussão interessante que tem a ver com as diferentes estratégias que podemos adotar é sobre listar apenas os UUIDs das entidades relacionadas ou **o objeto completo**.

Por exemplo, ao invés de:

```json
{
  "data": [
    {
      "id": "7c035edc-b329-11ef-935e-0242ac120004",
      "created_at": "2024-12-05T16:53:42Z",
      "updated_at": "2024-12-05T16:53:42Z",
      "is_active": true,
      "name": "Drama",
      "categories": [
        "f543a342-a4e1-11ef-9a8a-0242ac120003",
        "3b1c8387-a4ed-11ef-ad6d-0242ac120002"
      ]
    }
  ]
}
```

Poderíamos ter:

```json
{
  "data": [
    {
      "id": "7c035edc-b329-11ef-935e-0242ac120004",
      "created_at": "2024-12-05T16:53:42Z",
      "updated_at": "2024-12-05T16:53:42Z",
      "is_active": true,
      "name": "Drama",
      "categories": [
        {
          "id": "f543a342-a4e1-11ef-9a8a-0242ac120003",
          "created_at": "2024-12-05T16:53:42Z",
          "updated_at": "2024-12-05T16:53:42Z",
          "is_active": true,
          "name": "Filme"
        },
        {
          "id": "3b1c8387-a4ed-11ef-ad6d-0242ac120002",
          "created_at": "2024-12-05T16:53:42Z",
          "updated_at": "2024-12-05T16:53:42Z",
          "is_active": true,
          "name": "Documentário"
        }
      ]
    }
  ]
}
```

Mais uma vez, não tem certo nem errado e essa decisão pode guiar nossa estratégia também. Por exemplo, se quisermos sempre listar os objetos completos, faria mais sentido fazer o join entre os tópicos de gêneros e categorias, de modo que o **documento** indexado no Elasticsearch já possuiría todas as informações. Isso facilitaria coisas como, em `/videos`, se o `search` possuir o nome de uma **categoria**, esse vídeo seria retornado.

No nosso caso, estamos indo pelo caminho mais simples, mas é importante que você entenda todo o potencial do Elasticsearch e de como as decisões do nosso **negócio** também vão guiar nossas decisões de arquitetura de software.


# Aula 9.11 - Testes para ListGenre

- Criar `drama` e `romance` em conftest
  - drama com 2 categorias
  - romance sem categoria
- Atualizar o populated_es do conftest
- Atualizar o `es` em conftest para criar e deletar os indíces de genre


> Desafio: escrever o teste de API para o endpoint de `/genres`.
