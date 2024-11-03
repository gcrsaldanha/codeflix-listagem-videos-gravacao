# Módulo 3 - Elasticsearch Sink Connector

# Aula 3.1 - Criando o nosso banco Elasticsearch

Relembrando: esse não é um curso sobre Elasticsearch, temos um curso específico para isso. Nosso é integrar o Elasticsearch com o Kafka, utilizando o Elasticsearch Sink Connector.

Primeiro, vamos adicionar o Elasticsearch ao nosso docker-compose.yml, utilizando a [imagem oficial do Elasticsearch](https://hub.docker.com/_/elasticsearch):

```yaml
elasticsearch:
  container_name: elasticsearch
  hostname: elasticsearch
  image: docker.elastic.co/elasticsearch/elasticsearch:8.13.4
  ports:
    - "9200:9200"
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false
  healthcheck:
    test: [ "CMD", "curl", "-f", "http://localhost:9200" ]
    interval: 30s
    timeout: 10s
    retries: 5
  volumes:
    - elasticsearch-data:/usr/share/elasticsearch/data

volumes:
  elasticsearch-data:
```

Agora basta rodar o nosso container:

```bash
docker-compose up elasticsearch
```

Para verificar que o nosso serviço funciona, vamos criar um índice e um documento nesse índice:

```bash
curl -X PUT "localhost:9200/codeflix"

curl -X POST "localhost:9200/codeflix/_doc/1" -H 'Content-Type: application/json' -d'
{
  "title": "Elasticsearch Sink Connector",
  "description": "Curso de Elasticsearch Sink Connector"
}'

curl -X GET "localhost:9200/codeflix/_doc/1" | jq
```

Pronto, temos uma instância do Elasticsearch funcionando. É importante ressaltar que só criamos esse documento como exemplo, porque os documentos serão criados automaticamente pelo nosso Sink Connector. Vamos deletar o índice criado:

```bash
curl -X DELETE "localhost:9200/codeflix"
```

Se você quiser se aprofundar mais nas configurações para o Elasticsearch com Docker, você pode acessar o [guia oficial da Elastic](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html).
