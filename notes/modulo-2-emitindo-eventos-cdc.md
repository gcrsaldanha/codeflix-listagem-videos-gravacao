# Módulo 2 - Emitindo Eventos (CDC)

# 2.1 - Criando o nosso banco (MySQL)

Criar o `docker-compose.yml`:

```yaml
services:
  mysql:
    container_name: mysql
    hostname: mysql
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: codeflix
      MYSQL_USER: codeflix
      MYSQL_PASSWORD: codeflix
    healthcheck:
      test: [ "CMD", "mysqladmin", "ping", "-h", "localhost" ]
      interval: 30s
      timeout: 10s
      retries: 5
    volumes:
      - mysql-data:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  mysql-data:
```

Subir o container do MySQL:

```bash
docker compose up mysql
```

Conectar no MySQL como usuario `codeflix`:

```bash
docker compose exec -it mysql mysql --host 127.0.0.1 --port 3306 --user codeflix --password=codeflix --database=codeflix
```

Para facilitar, vamos adicionar isso ao `Makefile`:

```make
mysql:
	docker compose exec -it mysql mysql --host 127.0.0.1 --port 3306 --user codeflix --password=codeflix --database=codeflix
```

Agora basta executar `make mysql` para conectar no banco `codeflix` como usuario `codeflix`.

Para finalizar, vamos criar a nossa tabela `categories` e inserir 1 categoria:

```sql
DROP TABLE IF EXISTS categories;

CREATE TABLE categories
(
    id          VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name        VARCHAR(255) NOT NULL,
    description VARCHAR(255)            DEFAULT '',
    is_active   BOOLEAN                 DEFAULT TRUE,
    created_at  TIMESTAMP               DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP               DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO categories (name, description)
VALUES ('Filme', 'Categoria para longa-metragem')
;

SELECT *
FROM categories;
```

# 2.2 - Configurando o Kafka

Como esse curso não é um curso **sobre Kafka**, nós não vamos perder muito tempo com todos os detalhes de configuração (
que são muitos).

Se você pesquisou sobre o Kafka, você provavelmente já viu que a Confluent oferece serviços de hosting do Kafka. Porém,
para evitar termos que criar conta, free trial, essas coisas, achei melhor rodar o Kafka localmente em um container do
Docker.

Para isso, vamos utilizar de exemplo a configuração de single-node providencidada pela própria
Apache: [single-node](https://github.com/apache/kafka/blob/trunk/docker/examples/docker-compose-files/single-node/plaintext/docker-compose.yml)

```yaml
services:
  broker:
    image: apache/kafka:3.7.0
    hostname: broker
    container_name: broker
    ports:
      - '9092:9092'  # Porta interna (dentro da rede do Docker)
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: 'CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT'
      KAFKA_ADVERTISED_LISTENERS: 'PLAINTEXT_HOST://localhost:9092,PLAINTEXT://broker:19092'  # Porta utilizada para clientes externos se conectarem ao cluster
      KAFKA_PROCESS_ROLES: 'broker,controller'
      KAFKA_CONTROLLER_QUORUM_VOTERS: '1@broker:29093'
      KAFKA_LISTENERS: 'CONTROLLER://:29093,PLAINTEXT_HOST://:9092,PLAINTEXT://:19092'
      KAFKA_INTER_BROKER_LISTENER_NAME: 'PLAINTEXT'
      KAFKA_CONTROLLER_LISTENER_NAMES: 'CONTROLLER'
      CLUSTER_ID: '4L6g3nShT-eMCtK--X86sw'
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_LOG_DIRS: '/tmp/kraft-combined-logs'
```

Nesse mesmo repositório tem um arquivo
de [README](https://github.com/apache/kafka/blob/trunk/docker/examples/README.md#single-node) com mais detalhes sobre
como utilizar os exemplos provdenciados. Caso você queira testar outras configurações, recomendo olhar com calma as
configurações possíveis.

Modificações que fizemos:

- Definir a imagem `apache/kafka:3.7.0`.
- Adicionar env: `KAFKA_LOG4J_ROOT_LOGLEVEL: INFO`.
- Adicionar `healthcheck` para verificar se o Kafka está rodando.
- Adicionar o volume `kakfa-data` para persistir os dados do nosso container.
- Alterar nome do service "broker" para "kafka".

Agora basta rodar o comando `docker compose up kafka` para subir o container do Kafka.

```bash
docker compose up kafka
```

Podemos verificar que o nosso serviço Kafka está rodando com o comando:

```bash
docker compose ps
```

Observe o `(healthy)` - significa que o healthcheck funcionou. Também podemos executar manualmente:

```bash
docker compose exec -it kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092  --list
```

Esse comando não retorna nada porque não temos tópicos criados. Esses tópicos serão criados pelo próprio Debezium a
seguir.

Inclusive, é um bom momento para adicionar esse comando ao nosso Makefile.

# 2.3 - Configurando o Debezium

A arquitetura do Kafka possui um componente chamado Kafka Connect. Ele é um framework para conectar o Kafka com outras
fontes de dados (para consumir ou produzir dados).

Se olharmos o nosso diagrama C4, percebemos um container próprio do Kafka Connect que interage com:

- Broker Kafka
- MySQL
- Elasticsearch

O nosso objetivo é capturar as mudanças do MySQL e enviar para o Kafka. Para isso, vamos utilizar o Debezium.

Primeiro precisamos rodar um container com o Kafka Connect. Existem algumas imagens pré-configuradas, mas eu prefiro
utilizar a [imagem oficial do Debezium](https://hub.docker.com/r/debezium/connect). Vamos utilizar a versão 2.5.

```yaml
  connect:
    container_name: connect
    hostname: connect
    image: quay.io/debezium/connect:2.5
    ports:
      - "8083:8083"
    environment:
      BOOTSTRAP_SERVERS: kafka:19092  # Broker advertised listener
      GROUP_ID: 1
      CONFIG_STORAGE_TOPIC: my_connect_configs
      OFFSET_STORAGE_TOPIC: my_connect_offsets
      STATUS_STORAGE_TOPIC: my_connect_statuses
      CONFIG_STORAGE_REPLICATION_FACTOR: 1
      OFFSET_STORAGE_REPLICATION_FACTOR: 1
      STATUS_STORAGE_REPLICATION_FACTOR: 1
      CONNECT_PLUGIN_PATH: /kafka/connect,/kafka/extra-plugins
    healthcheck:
      test: [ "CMD", "curl", "-f", "http://localhost:8083/connectors" ]
      interval: 30s
      timeout: 10s
      retries: 5
    depends_on:
      kafka:
        condition: service_healthy
      mysql:
        condition: service_healthy
    volumes:
      - ./kafka-connect/connect-plugins:/kafka/extra-plugins
```

No [Docker Hub do Debezium](https://hub.docker.com/r/debezium/connect) tem uma sessão "Environment variables" que
explica o que cada variável de ambiente faz.
A configuração `CONNECT_PLUGIN_PATH` vai ser explicada quando formos adicionar o conector do Elasticsearch.

Vamos subir o container do Kafka Connect:

```bash
docker compose up connect
```

Se tudo der certo, você vai ver alguma mensagem com: `Finished starting connectors and tasks`. Além disso, o Kafka
Connect criou alguns tópicos: `my_connect_configs`, `my_connect_offsets` e `my_connect_statuses`.

```
make list-topics
```

Nós geralmente não interagimos diretamente com esses tópicos, mas eles são essenciais para o funcionamento do Kafka
Connect.

Para interagir com o Kafka Connect, nós utilizamos a API REST. Por exemplo, para listar todos os connectors, podemos
fazer um GET:

```bash
curl -X GET http://localhost:8083/connectors
```

Precisamos agora registrar o Debezium MySQL Connector - ou seja, o connector que vai consumir as mudanças do MySQL e
enviar para o Kafka.

```bash
curl -i -X POST -H "Accept: application/json" -H "Content-Type: application/json" localhost:8083/connectors/ -d '{
  "name": "debezium",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "mysql",
    "database.port": "3306",
    "database.user": "root",
    "database.password": "root",
    "topic.prefix": "catalog-db",
    "database.server.id": "1",
    "database.include.list": "codeflix",
    "schema.history.internal.kafka.bootstrap.servers": "kafka:19092",
    "schema.history.internal.kafka.topic": "schema-history.catalog-db"
  }
}'
```

A documentação do confluent possui uma sessão sobre
a [configuração do Debezium MySQL Connector](https://docs.confluent.io/kafka-connectors/debezium-mysql-source/current/mysql_source_connector_config.html)

Se tudo der certo, você vai ver uma resposta com status 201 e o nome do connector que você acabou de criar.

```bash
HTTP/1.1 201 Created
Date: Sat, 02 Nov 2024 19: 59: 15 GMT
Location: http: //localhost:8083/connectors/debezium
Content-Type: application/json
Content-Length: 454
Server: Jetty(9.4.52.v20230823)

{... informações sobre o connector ...}
```

Para verificar se o connector foi criado, podemos listar os connectors registrados:

```bash
curl localhost:8083/connectors/
```

E obter mais informações sobre o connector em si:

```bash
curl localhost:8083/connectors/debezium | jq
```

Também, novos tópicos foram criados:

```
# make list-topics
...
catalog-db
catalog-db.codeflix.categories
schema-history.catalog-db
```

`catalog-db` e `schema-history.catalog-db` armazenam informações sobre o banco de dados e as mudanças de schema,
respectivamente.
`catalog-db.codeflix.categories` armazena as mudanças da tabela `categories`, que é o tópico mais relevante para a
gente.

Vamos analisar as mensagens nesse tópico:

```bash
docker compose exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh --topic catalog-db.codeflix.categories --from-beginning --bootstrap-server localhost:9092
```

```json
{
  "schema": {...},
  "payload": {
    "before": null,
    "after": {
      "id": "9c970d4d-995a-11ef-a165-0242ac130002",
      "name": "Filme",
      "description": "Categoria para longa-metragem",
      "is_active": 1,
      "created_at": "2024-11-02T20:39:52Z",
      "updated_at": "2024-11-02T20:39:52Z"
    },
    "source": {...},
    "op": "c",
    "ts_ms": 1730579992514,
    "transaction": null
  }
}
```

Pontos importantes:
- payload: corpo da mensagem.
- before/after: estado anterior e atual da "linha" no banco de dados.
- op: operação realizada (c = create, u = update, d = delete).

Pronto, agora conseguimos capturar as mudanças do MySQL e enviar para o Kafka.


# Desafio: Atualizar a tabela e observar as mudanças

- Script para registar o debezium connector: [register-debezium-connector.sh](../kafka-connect/bin/register-debezium-connector.sh)
- Docker compose atualizado: [docker-compose.yml](../docker-compose.yml)

Mantenha uma janela do terminal consumindo eventos do tópico `catalog-db.codeflix.categories`.

Insira novas informações na tabela, atualize e observe as mudanças no tópico `catalog-db.codeflix.categories`.
```sql
INSERT INTO categories (name, description) VALUES ('Filme 2', 'Categoria para longa-metragem 2');
```

Atualize alguma informação na tabela `categories`:

```sql
UPDATE categories SET name = 'Filme 2' WHERE name = 'Filme';
```

Remova alguma informação na tabela `categories`:

```sql
DELETE FROM categories WHERE name = 'Filme 2';
```

Observe as mensagens que aparecem e verifique se faz sentido com o que você fez no banco de dados.
