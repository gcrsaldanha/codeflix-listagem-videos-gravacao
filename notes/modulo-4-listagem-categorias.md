# Módulo 4 - Listagem de Categorias

# Aula 4.1 - Introdução à nossa API

Vocês vão perceber que esse projeto, ao contrário do outro que possuía muitas regras de negócio e casos de uso, é bem
mais simples. Por exemplo, para todas nossas entidades temos apenas 1 caso de uso: **listagem**.

Essa listagem vai ser construída em cima do nosso banco de dados sincronizado pelo Debezium, exposta via API HTTP para o
usuário, e permitir que o usuário realize paginação, ordenação e filtro nas entidades.

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

# Aula 4.2 - Criando Category Domain

Ao contrário da parte 1 desse projeto (Administração de Catálogo), aqui as alterações em nossas entidades ocorrerão
apenas por meio do Debezium. Portanto, não precisamos nos preocupar com muitas regras de negócio além de validações
básicas.

Para facilitar essa parte de validações e diminuir a quantidade de código que precisamos escrever, vamos utilizar a
biblioteca `pydantic`.

Primeiro, vamos criar um ambiente virtual (mais para a frente vamos dockerizar nossa aplicação), recomendo utilizar o
Python 3.12 (é o que utilizarei ao longo do curso).

```bash
python -m venv .venv
source .venv/bin/activate
```

Agora, instale a biblioteca `pydantic`:

```bash
pip install pydantic
```

Por fim, vamos criar uma pasta `src` e o arquivo [`category.py`](../src/category.py).

> Não vamos entrar em muitos detalhes sobre o `pydantic`, mas recomendo muito a leitura
> da [documentação oficial](https://docs.pydantic.dev/latest/). Pense nele como um `dataclass` mais elaborado.

O legal do pydantic é que ele utiliza a sintaxe de type hints do Python para inferir o tipo dos campos, e com isso, ele
consegue fazer validações de tipos e valores automaticamente.

Por exemplo:

```python
from src.category import Category

category = Category(
    id='123e4567-e89b-12d3-a456-426614174000',
    name='Category Name',
    description='Category Description',
    is_active=True,
    created_at='2023-01-01T00:00:00',
    updated_at='2023-01-01T00:00:00'
)

print(category)

invalid_category = Category(id=1, name=120)

"""
ValidationError: 5 validation errors for Category
id
  UUID input should be a string, bytes or UUID object [type=uuid_type, input_value=1, input_type=int]
    For further information visit https://errors.pydantic.dev/2.9/v/uuid_type
name
  Input should be a valid string [type=string_type, input_value=120, input_type=int]
    For further information visit https://errors.pydantic.dev/2.9/v/string_type
created_at
  Field required [type=missing, input_value={'id': 1, 'name': 120}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.9/v/missing
updated_at
  Field required [type=missing, input_value={'id': 1, 'name': 120}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.9/v/missing
is_active
  Field required [type=missing, input_value={'id': 1, 'name': 120}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.9/v/missing
"""
```

# Aula 4.3 - Criando Category Repository

Assumindo que temos `categories` persistidas em um banco de dados, vamos criar um repositório para acessar esses dados.
E apesar de sabermos que estamos utilizando o Elasticsearch como banco de dados, vamos definir uma interface para seguir
o princípio da Inversão de Dependência.

Nossa interface `CategoryRepository` vai ter um único método: `search`.

[category_repository.py](../src/category_repository.py)

Toda a paginação/filtro/ordenação será delegada para o próprio banco de dados (geralmente mais eficiente). Por isso
definimos essa interface.

Essa implementação vai ficar mais para frente, quando implementarmos a integração com o Elasticsearch através de uma
classe que extenda `CategoryRepository`, por exemplo, `ElasticsearchCategoryRepository`.

# Aula 4.4 - List Category Use Case

Por enquanto teremos apenas 1 caso de uso para cada entidade, o de listagem. Vamos precisar definir alguns objetos:

- Input
- Output
    - Data
    - Metadata
      - Page
      - Per Page
      - Sort
      - Direction

E para ter uma melhor performance, vamos delegar toda a parte de paginação, busca e ordenação para o banco de dados. Especialmente por estarmos utilizando o Elasticsearch que é muito eficiente nesse tipo de operação.

Isso faz com que a lógica da nossa camada de aplicação se mantenha bem simples, praticamente passando os valores do input do usecase para o repository, e garantindo que o `input` seja válido (e.g.: SortableFields).

* Fazer TDD com o test em [test_list_category.py](../src/test_list_category.py)
* Implementação: [list_category.py](../src/list_category.py)

**Exercício**

1. Escrever um teste para a listagem com o `Input` contendo valores definidos para `page`, `per_page`, `sort` e `direction`.
2. Escrever um teste para garantir que caso o usuário passe um valor inválido para `sort`, o sistema retorne um erro.
