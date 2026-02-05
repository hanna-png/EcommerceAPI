.PHONY: up down build migrate test dump-dev restore-dev

# Start all containers in background (api, db, adminer, etc.)
up:
	docker compose up -d

# Build images and start containers
build:
	docker compose up -d --build

# Stop all containers
down:
	docker compose down

# Apply all Alembic migrations to the dev database
migrate:
	docker compose exec api poetry run alembic upgrade head

# Run all tests inside the api container
test:
	docker compose exec api poetry run pytest -q

# Create a dump of the dev database
dump-dev:
	docker compose exec db sh -lc 'pg_dump -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -Fc -f /dumps/dev.dump'

# Restore the dev database from the last dump
restore-dev:
	docker compose exec db sh -lc 'pg_restore -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" --clean --if-exists /dumps/dev.dump'
# Create a new Alembic migration from model changes
revision:
	docker compose exec api poetry run alembic revision --autogenerate -m "$(m)"
