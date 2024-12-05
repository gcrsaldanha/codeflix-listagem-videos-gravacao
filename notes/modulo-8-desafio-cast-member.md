# Módulo 8 - Desafio Cast Member

# Aula 8.1 - Desafio: Listagem de Cast Member

O objetivo deste desafio é implementar a listagem de Cast Members. Para isso, você vai precisar fazer os mesmos passos
que fizemos para a listagem de categorias.

## Criar tabela MySQL

1. Criar tabela `cast_members` no banco de dados para armazenar os dados de Cast Member e inserir alguns dados.

```mysql
CREATE TABLE cast_members
(
    id         VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name       VARCHAR(255) NOT NULL,
    type       VARCHAR(255) NOT NULL,
    is_active  BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## Registrar Debezium Source connector

1. Reiniciar o Kafka e Kafka Connect e registrar o Debezium Source Connector.
    - Ver anotações do [Módulo 2](modulo-2-emitindo-eventos-cdc.md)
2. Verificar que o tópico para `cast_members` foi criado: `catalog-db.codeflix.cast_members`.
   ```
   make list-topics  # ou docker compose exec -it kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
   ```
3. Verificar que as alterações no MySQL na tabela `cast_members` foram enviadas para o
   tópico `catalog-db.codeflix.cast_members`.
   Fazer inserções no MySQL e verificar se os dados foram enviados para o tópico.
    ```bash
    docker compose exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh --topic  catalog-db.codeflix.cast_members --from-beginning --bootstrap-server localhost:9092
    ```

## Registrar Elasticsearch Sink connector

1. Registrar o Elasticsearch Sink Connector consumindo o tópico `catalog-db.codeflix.cast_members`.
    ```bash
   curl -i -X POST -H "Accept: application/json" -H "Content-Type: application/json" localhost:8083/connectors/ -d '{
     "name": "elasticsearch",
     "config": {
       "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
       "tasks.max": "1",
       "topics": "catalog-db.codeflix.categories, catalog-db.codeflix.cast_members",  # Adicionar o tópico cast_members
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

> Talvez seja necessário remover o connector antes

   ```bash
   curl -X DELETE localhost:8083/connectors/elasticsearch
   ```

A partir daqui, você deve ser capaz de fazer alterações no banco de dados e popular o Elasticsearch com os dados de Cast Members.


## Domain: Cast Member

A entidade `CastMember` deve ter as seguintes especificações (além dos atributos de `Entity`):

- name: string
- type: "ACTOR" ou "DIRECTOR"

## Use Case / Repository / API

Com a nossa infraestrutura configurada, basta agora implementar o Use Case, Repository e API para listar os Cast Members.

Essa implementação vai ser muito parecida com a de categorias.
