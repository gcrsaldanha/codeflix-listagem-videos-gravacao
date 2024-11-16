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
