mysql:
	docker compose exec -it mysql mysql --host 127.0.0.1 --port 3306 --user codeflix --password=codeflix --database=codeflix

list-topics:
	docker compose exec -it kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
