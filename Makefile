.PHONY: build up down logs test clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down -v

logs:
	docker-compose logs -f

test:
	python e2e_tests/test_saga_workflow.py

clean:
	docker-compose down -v --rmi all --remove-orphans
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
