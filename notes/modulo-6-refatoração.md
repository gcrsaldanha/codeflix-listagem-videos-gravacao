# Módulo 6 - Refatoração

# Aula 6.1 - Executando testes com Docker

É interessante que a gente também possa executar nossos testes através de um docker container. Isso facilitar a
utilização do projeto por outros desenvolvedores e também evita que a gente precise se preocupar em rodar a nossa
infraestrutura antes de executar os testes.

Por exemplo, atualmente precisamos rodar o Elasticsearch antes de rodar os testes. 

Como futuramente também vamos executar o nosso projeto como um Docker container, vamos criar logo um Dockerfile bem simples:

```dockerfile
FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./src /app/src
```

Criar o arquivo [requirements.txt](../requirements.txt)
```requirements
elasticsearch==8.13.2
pydantic==2.9.2
pytest==8.3.3
```

Adicionar o service `tests` ao docker-compose.yml:

```
tests:
build: .
environment:
  PYTHONPATH: "/app"
  ELASTICSEARCH_TEST_HOST: "http://elasticsearch-test:9200"  # elasticsearch-test ao inves de localhost!
container_name: tests
command: [ "pytest", "-vv", "-s"]
depends_on:
  elasticsearch-test:
    condition: service_healthy
profiles:
  - test  # subir junto com o elasticsearch-test
ports:
  - "5678:5678"  # Expor uma porta para o debugger no host
volumes:
  - .:/app
```

Agora conseguimos rodar os testes com ambos comandos:

```bash
pytest  # Host / venv
docker compose run --rm tests
```

> Testar parar o container elasticsearch-test e rodar os testes com o comando `docker compose run --rm tests`.


# Aula 6.2 - Reorganizando pastas

Tem muitas maneiras de organizar as nossas pastas. Como nossa aplicação praticamente não tem regra de negócio, a gente vai separar por **camadas** e não por **domínio**.

```
src
├── application
│   └── list_category.py
├── domain
│   ├── category.py
│   └── category_repository.py
├── infra
│   └── elasticsearch
│       └── elasticsearch_category_repository.py
└── tests
    ├── integration_tests
    │   ├── test_elasticsearch_category_repository.py
    │   └── test_list_category.py
    └── unit_tests
        └── test_list_category.py
```

# Aula 6.3 - Criando nossa Entity

- Criar [`Entity`](../src/domain/entity.py) e fazer Category herdar dela.


# Aula 6.4 - Abstraindo listagem de entidades com generics

Essa aula vai ser um pouco maior porque para abstrair e utilizar os generics em um lugar, acabamos precisando ajustar em vários outros lugares.

Vamos abstrair o usecase de listagem para que a gente possa reutilizá-lo em outras entidades.

Criar o [`list_entity.py`](../src/application/list_entity.py)

Criar o [`repository.py`](../src/domain/repository.py) genérico.
    Atualizar o uso de `CategoryRepository` -> `CategoryRepository(Repository[Category], ABC): pass`

ListEntity precisa retornar um `ListOutput[T]`, então precisamos criar o `ListOutput`.
Criar o arquivo [`listing.py`](../src/application/listing.py)
1. Mover `DEFAULT_PAGINATION_SIZE` e `SortDirection` para esse arquivo.
2. Criar o `ListOutputMeta` (sem generics) e substituir `ListCategoryOutputMeta` por ele.
3. Criar o `ListOutput[T: Entity]` com generics. Substituir
4. O `ListInput` é um pouco mais complicado pois a parte genérica dele é o argumento `sort`:

```python
class ListInput[SortableFieldsType: StrEnum](BaseModel):
    search: str | None = None
    page: int = 1
    per_page: int = DEFAULT_PAGINATION_SIZE
    sort: SortableFieldsType | None = None
    direction: SortDirection = SortDirection.ASC
```

E atualizar o `ListCategoryInput` para usar o `ListInput` genérico:
```python
class ListCategoryInput(ListInput[CategorySortableFields]):
    sort: CategorySortableFields | None = CategorySortableFields.NAME
```

Por fim, vamos verificar se nosso testes estão passando e o que precisamos corrigir.

- Adicionar um teste unitário para `ListCategory` para confirmar que nossa validação de Input continua funcionando mesmo com tipos genéricos: `test_list_with_invalid_sort_field_raises_error`
- Também podemos executar no shell e na própria IDE para verificar que nosso código está funcionando corretamente.

Agora já deve ser possível ver como é trivial adicionar a listagem para uma nova entidade, por exemplo, `Genre`.
