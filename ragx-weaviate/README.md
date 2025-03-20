# Basic RAG app using Weaviate

## Prerequisites
- Before we get started, install Docker and Ollama on your machine.
- Then, download the nomic-embed-text and llama3.2 models by running the following command:
```commandline
ollama pull nomic-embed-text
ollama pull llama3.2
```

## Set up Weaviate
- Run the following command to start a Weaviate instance using Docker:
```
docker-compose up -d
```
- Install the latest, Python client v4, by adding weaviate-client to your Python environment with pip:
```commandline
pip install -U weaviate-client
```