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
