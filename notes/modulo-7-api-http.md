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
