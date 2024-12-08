# Módulo 7 - API HTTP

# Aula 7.1 - Configurando nossa API HTTP

Instalar o fastapi:

```bash
pip install "fastapi[standard]"
```

Criar o arquivo [`main.py`](../src/infra/api/http/main.py) com uma rota simples `/categories`

Executar o servidor:

```bash
fastapi dev src/infra/api/http/main.py --host 0.0.0.0 --port 8000 --reload
```

Verificar que a rota `/categories` está funcionando.


# Aula 7.2 - Executando o servidor HTTP com Docker

Adicionar o service `fastapi` ao nosso `docker-compose.yml`

```dockerfile
  fastapi:
    build: .
    container_name: fastapi
    hostname: fastapi
    environment:
      PYTHONPATH: "/app"
      ELASTICSEARCH_HOST: "http://elasticsearch:9200"
    ports:
      - "8000:8000"
    command: fastapi dev src/infra/api/http/main.py --host 0.0.0.0 --port 8000 --reload;
    depends_on:
      elasticsearch:
        condition: service_healthy
    healthcheck:
      test: [ "CMD", "curl", "-f", "http://localhost:8000/healthcheck/" ]
      interval: 30s
      timeout: 10s
      retries: 5
```

Adicionar `fastapi[standard]==0.115.4` em `requirements.txt`.

Fazer o build do container:

```bash
docker compose build
```

Executar o container:

```bash
docker compose up fastapi
```

Criar a rota de healthcheck:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/healthcheck/")
def healthcheck():
    return {"status": "ok"}
```


Verificar que o autoreload está funcionando: adicionar uma Category fake e recarregar a página.


# Aula 7.3 - Rota /categories

Simplesmente adicionar a rota:
```python
@app.get("/categories", response_model=ListOutput[Category])  # Observer o generics sendo usado aqui
def list_categories():
    return ListCategory(repository=ElasticsearchCategoryRepository()).execute(ListCategoryInput())
```

O uso de `response_model` serve tanto para documentação quanto para serialização do objeto de resposta.

Vamos ver a documentação gerada automaticamente através da tipagem: http://localhost:8000/docs

Experimente remover o `[Category]` da annotation e ver a diferença.

Vamos adicionar pelo menos um teste end-to-end para essa rota simples:

```python
# tests/e2e_test/test_list_category_api.py
from fastapi.testclient import TestClient

from src.infra.api.http.main import app

def test_list_categories_empty_response():
    client = TestClient(app=app)
    response = client.get("/categories")
    assert response.status_code == 200
    assert response.json() == {
        "data": [],
        "meta": {
            "page": 1,
            "per_page": 5,
            "sort": "name",
            "direction": "asc",
        }
    }

```

Esse teste vai falhar por um dos dois motivos:
- Se o container `elasticsearch` estiver rodando e este possuir dados, o teste vai falhar porque a resposta não é vazia.
- Se o container `elasticsearch` não estiver rodando, o teste vai falhar porque a API não vai conseguir se conectar ao Elasticsearch.

Nós precisamos garantir que nosso teste utilize o elasticsearch de teste, parecido com o que fizemos anteriormente. Vamos resolver isso e escrever mais testes a seguir.


# Aula 7.4 - Testando a rota /categories

Utilizar injeção de dependência do FastAPI para passar o ElasticsearchCategoryRepository como dependência da rota `/categories`.

```python
from fastapi import FastAPI, Depends

from src.infra.api.http.repositories.elasticsearch_category_repository import ElasticsearchCategoryRepository

app = FastAPI()

def get_repository() -> CategoryRepository:
    return ElasticsearchCategoryRepository()

@app.get("/categories", response_model=ListOutput[Category])
def list_categories(repository: ElasticsearchCategoryRepository = Depends(get_repository)):
    return ListCategory(repository=repository).execute(ListCategoryInput())
```

> Se quiser aprender mais sobre injeção de dependência no FastAPI, veja a documentação oficial: https://fastapi.tiangolo.com/tutorial/dependencies/. E sobre DI em testes: https://fastapi.tiangolo.com/advanced/testing-dependencies/

Escrever o teste com override da dependência:

```python
@pytest.fixture
def populated_category_repository(
    populated_es: Elasticsearch,
) -> Iterator[CategoryRepository]:
    yield ElasticsearchCategoryRepository(client=populated_es)


@pytest.fixture
def client_with_populated_repo(
    populated_category_repository: CategoryRepository,
) -> Iterator[TestClient]:
    app.dependency_overrides[get_category_repository] = lambda: populated_category_repository
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_list_categories(
    test_client_with_populated_repo: TestClient,
    series: Category,
    movie: Category,
    documentary: Category,
) -> None:
    response = test_client_with_populated_repo.get("/categories")
    assert response.status_code == 200
    assert response.json() == {...}

```

Também vamos criar um `conftest.py` com o nosso repositório do Elasticsearch, e substituir o uso em outros testes. Ver arquivo: [src/tests/conftest.py](../src/tests/conftest.py) Podemos colocar outras fixtures nesse arquivo também.

# Aula 7.5 - Query params na rota /categories

Adicionar query params na rota `/categories`.
Adicionar unit tests simples: [test_list_category_api.py](../src/tests/unit_tests/test_list_category_api.py)
