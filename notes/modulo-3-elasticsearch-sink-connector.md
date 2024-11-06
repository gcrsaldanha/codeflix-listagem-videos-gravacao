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

# Aula 3.2 - Configurando o Elasticsearch Sink Connector pt. 1

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

Também é possível acessar pelo navegador.

# Aula 3.3 - Configurando o Elasticserach Sink Connector pt. 2

Se você visualizou os dados persistidos no Elasticsearch, vai percerber que eles foram salvos no mesmo formato que estavam no Kafka topic:

```
{
  "before": null,
  "after": {...},
  "source": {...},
  ...
}
```

Nós não precisamos de todas essas informações no nosso banco de dados, gostaríamos apenas de manter os valores da entidade, como:

```json
{
    "id": "afbf306c-994a-11ef-8f71-0242ac130002",
    "name": "Filme",
    "description": "Categoria para longa-metragem",
    "is_active": 1,
    "created_at": "2024-11-02T18:45:52Z",
    "updated_at": "2024-11-02T18:45:52Z"
}
```

Para isso, vamos precisar configurar o nosso Elasticsearch Sink Connector com mais algumas propriedades:

```bash
curl -i -X POST -H "Accept: application/json" -H "Content-Type: application/json" localhost:8083/connectors/ -d '{
  "name": "elasticsearch",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "1",
    "topics": "catalog-db.codeflix.categories",
    "connection.url": "http://elasticsearch:9200",
    "behavior.on.null.values": "delete",
    "key.ignore": "false",
    "transforms": "unwrap,key,cast",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones": "false",
    "transforms.unwrap.drop.deletes": "false",
    "transforms.key.type": "org.apache.kafka.connect.transforms.ExtractField$Key",
    "transforms.key.field": "id",
    "transforms.cast.type": "org.apache.kafka.connect.transforms.Cast$Value",
    "transforms.cast.spec": "is_active:boolean",
    "errors.tolerance": "all",
    "errors.deadletterqueue.topic.name":"dlq_elastic_sink",
    "errors.deadletterqueue.topic.replication.factor": 1,
    "errors.deadletterqueue.context.headers.enable": "true",
    "errors.log.enable": "true"
  }
}'
```

- `transforms`: define os tipos de transformações que faremos nos dados:
  - `unwrap`: extrair o "after" ao invés de toda mensagem
  - `key`: utilizar o campo `id` da mensagem como `key` no Elasticsearch
  - `cast`: converter o campo `is_active` (0, 1) para booleano

> Mais detalhes sobre configurações podem ser encontrados na documentação do [Elasticsearch Sink Connector](https://docs.confluent.io/kafka-connectors/elasticsearch/current/overview.html) ou do próprio [Apache Kafka Connect](https://kafka.apache.org/documentation/#connectconfigs).

Na verdade, antes de rodar o comando acima, é necessário deletar o conector anterior:

```bash
curl -X DELETE localhost:8083/connectors/elasticsearch
```

Agora podemos registrar o nosso connector novamente e verificar como os dados são inseridos no Elasticsearch.

```sql
INSERT INTO categories (name) VALUES "teste";
```

Verificar o novo documento no Elasticsearch:

```bash
curl -X GET "localhost:9200/catalog-db.codeflix.categories/_search" | jq
```

Resposta:

```json
{
  "_index": "catalog-db.codeflix.categories",
  "_id": "2db70700-9b0d-11ef-9c37-0242ac130002",
  "_score": 1.0,
  "_source": {
    "id": "2db70700-9b0d-11ef-9c37-0242ac130002",
    "name": "Teste",
    "description": "",
    "is_active": true,
    "created_at": "2024-11-05T00:30:37Z",
    "updated_at": "2024-11-05T00:30:37Z"
  }
}
```

> Verificar que alterações no banco de dados MySQL (CRUD) são refletidas no Elasticsearch!


# Aula 3.4 - Inicialização Kafka Connect

Para facilitar o nosso desenvolvimento e não ter que ficar manualmente rodando o connector toda vez que reiniciarmos o nosso Kafka Broker, vamos criar um serviço no nosso docker-compose.yml para inicializar o Kafka Connect e registrar os connectors.

```yaml
connect-setup:
  container_name: connect-setup
  image: curlimages/curl
  volumes:
    - ./kafka-connect/bin:/kafka-connect/bin
  depends_on:
    connect:
      condition: service_healthy
  command: [ "sh", "-c", "chmod +x /kafka-connect/bin/connect-setup.sh && /kafka-connect/bin/connect-setup.sh" ]
  restart: "no"
```

E vamos precisar criar o arquivo `connect-setup.sh` na pasta host: kafka-connect/bin:

- [connect-setup.sh](../kafka-connect/bin/connect-setup.sh)

Precisamos criar os arquivos `debezium-source.json` e `elasticsearch-sink.json` na pasta host: kafka-connect/bin:

- [debezium-source.json](../kafka-connect/bin/debezium-source.json)
- [elasticsearch-sink.json](../kafka-connect/bin/elasticsearch-sink.json)
