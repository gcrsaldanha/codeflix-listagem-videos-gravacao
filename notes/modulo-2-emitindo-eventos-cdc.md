# Módulo 2 - Emitindo Eventos (CDC)

# 2.1 - Criando o nosso banco (MySQL)

Criar o `docker-compose.yml`:
```
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

CREATE TABLE categories (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255) DEFAULT '',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO categories (name, description)
VALUES
    ('Filme', 'Categoria para longa-metragem')
;

SELECT * FROM categories;
```

# 2.2 - Configurando o Kafka

Como esse curso não é um curso **sobre Kafka**, nós não vamos perder muito tempo com todos os detalhes de configuração (que são muitos).

Se você pesquisou sobre o Kafka, você provavelmente já viu que a Confluent oferece serviços de hosting do Kafka. Porém, para evitar termos que criar conta, free trial, essas coisas, achei melhor rodar o Kafka localmente em um container do Docker.

Para isso, vamos utilizar de exemplo a configuração de single-node providencidada pela própria Apache: [single-node](https://github.com/apache/kafka/blob/trunk/docker/examples/docker-compose-files/single-node/plaintext/docker-compose.yml)
```dockerfile
version: '2'
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

Nesse mesmo repositório tem um arquivo de [README](https://github.com/apache/kafka/blob/trunk/docker/examples/README.md#single-node) com mais detalhes sobre como utilizar os exemplos provdenciados. Caso você queira testar outras configurações, recomendo olhar com calma as configurações possíveis.

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

Esse comando não retorna nada porque não temos tópicos criados. Esses tópicos serão criados pelo próprio Debezium a seguir.

Inclusive, é um bom momento para adicionar esse comando ao nosso Makefile.
