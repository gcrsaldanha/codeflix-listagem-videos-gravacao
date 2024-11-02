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
