# Módulo 4 - Listagem de Categorias

# Aula 4.1 - Introdução à nossa API

Vocês vão perceber que esse projeto, ao contrário do outro que possuía muitas regras de negócio e casos de uso, é bem mais simples. Por exemplo, para todas nossas entidades temos apenas 1 caso de uso: **listagem**.

Essa listagem vai ser construída em cima do nosso banco de dados sincronizado pelo Debezium, exposta via API HTTP para o usuário, e permitir que o usuário realize paginação, ordenação e filtro nas entidades.

> Exibir API de /categories rodando em localhost. Listagem, Busca, Ordenação e Paginação.

Request
```bash
curl -X GET http://localhost:8000/categories/?page=1&per_page=1&sort=name&direction=desc?search=Filme
```

Response
```json
{
  "data": [
    {
      "id": "612d586b-575f-11ef-8236-0242ac120005",
      "created_at": "2024-08-10T21:27:43Z",
      "updated_at": "2024-08-10T21:27:43Z",
      "is_active": true,
      "name": "Filme",
      "description": "Categoria para longa-metragem"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 1,
    "sort": "name",
    "direction": "desc"
  }
}
```
