# Módulo 3 - Elasticsearch Sink Connector

# Aula 3.1 - Criando o nosso banco Elasticsearch

Relembrando: esse não é um curso sobre Elasticsearch, temos um curso específico para isso. Nosso é integrar o
Elasticsearch com o Kafka, utilizando o Elasticsearch Sink Connector.

Primeiro, vamos adicionar o Elasticsearch ao nosso docker-compose.yml, utilizando
a [imagem oficial do Elasticsearch](https://hub.docker.com/_/elasticsearch):

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

Pronto, temos uma instância do Elasticsearch funcionando. É importante ressaltar que só criamos esse documento como
exemplo, porque os documentos serão criados automaticamente pelo nosso Sink Connector. Vamos deletar o índice criado:

```bash
curl -X DELETE "localhost:9200/codeflix"
```

Se você quiser se aprofundar mais nas configurações para o Elasticsearch com Docker, você pode acessar
o [guia oficial da Elastic](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html).

# Aula 3.2 - Configurando o Elasticsearch Sink Connector

Agora que temos o nosso Elasticsearch funcionando, vamos configurar o
nosso [Elasticsearch Sink Connector](https://www.confluent.io/hub/confluentinc/kafka-connect-elasticsearch).

Se você observar como configuramos o Debezium, passamos a classe `io.debezium.connector.mysql.MySqlConnector`. O Connect
reconhecia essa classe porque a imagem que utilizamos já tinha essa classe disponível. No caso do Elasticsearch Sink
Connector, precisamos baixar a imagem que contém essa classe e adicioná-la ao nosso container.

A imagem pode ser baixada aqui: https://www.confluent.io/hub/confluentinc/kafka-connect-elasticsearch, na opção "Self-Hosted".

> Se você utiliza o Confluent Cloud / Platform para rodar o Kafka/Connect, você não precisa baixar a imagem. Basta
> seguir as instruções de como adicionar o Elasticsink Connector.

Após realizar o download, extraia a pasta dentro de `./kafka-connect/connect-plugins` (pasta criada quando configuramos
o volume do Kafka Connect).

Para isso, vamos executar aquele mesmo comando que utilizamos para configurar o Debezium, mas agora para o Elasticsearch
Sink Connector:

> Verifique que o seu container do Kafka Connect está rodando.

```bash
curl -i -X POST -H "Accept: application/json" -H "Content-Type: application/json" localhost:8083/connectors/ -d '{
  "name": "elasticsearch",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "1",
    "topics": "catalog-db.codeflix.categories",
    "connection.url": "http://elasticsearch:9200",
    "key.ignore": "true"  // Elasticsearch vai ignorar a chave do Kafka e criar uma própria para cada documento
  }
}'
```

Para ver todas as configurações do Elasticsearch Sink Connector, você pode acessar
a [documentação oficial](https://docs.confluent.io/kafka-connectors/elasticsearch/current/configuration_options.html).

Agora podemos acessar o nosso Elasticsearch e verificar que o índice foi criado, e os documentos inseridos:

```bash
curl -X GET "localhost:9200/catalog-db.codeflix.categories/_search" | jq
```
