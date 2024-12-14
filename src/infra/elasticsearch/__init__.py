import os

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
ELASTICSEARCH_HOST_TEST = os.getenv("ELASTICSEARCH_TEST_HOST", "http://localhost:9201")
