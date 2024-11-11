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

# Aula 6.3 - Abstraindo Category: Domain

- Criar [`Entity`](../src/domain/entity.py) e fazer Category herdar dela.
