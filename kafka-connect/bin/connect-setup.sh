#!/bin/sh
echo "Kafka Connect started. Registering Debezium connector..."

printf "Registering Debezium connector...\n"
curl -X POST -H "Accept: application/json" -H "Content-Type: application/json" http://connect:8083/connectors/ -d @/kafka-connect/bin/debezium-source.json
printf "Debezium connector registered.\n\n"


printf "Registering Elasticsearch Sink connector...\n"
curl -X POST -H "Accept: application/json" -H "Content-Type: application/json" http://connect:8083/connectors/ -d @/kafka-connect/bin/elasticsearch-sink.json
printf "Elasticsearch Sink connector registered.\n\n"
