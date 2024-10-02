.PHONY: run run-docker docker-up docker-down docker-build

# Default settings
TYPE ?= admin
IP ?= 127.0.0.1
PORT ?= 8000
BOOTSTRAP ?=

# Local Python run
run:
	python src/main.py --type $(TYPE) -i $(IP) -p $(PORT) $(BOOTSTRAP)

# Docker run
run-docker:
	docker run -d --name $(TYPE)_node_$(PORT) -p $(PORT):$(PORT) distribiuted-scrapper:latest --type $(TYPE) --ip 0.0.0.0 --port $(PORT) $(BOOTSTRAP)


# Start services using Docker Compose
docker-up:
	docker-compose up -d

# Stop services using Docker Compose
docker-down:
	docker-compose down

# Build or rebuild services
docker-build:
	docker build -t distribiuted-scrapper:latest .