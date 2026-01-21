.PHONY: up down build test migrate migrate-test dump-dev dump-test restore-dev restore-test list-dbs

up:
	docker compose up -d

build:
	docker compose up -d --build

down:
	docker compose down

list-dbs:
	docker compose exec db psql -U $${POSTGRES_USER} -d postgres -c "\l"

migrate:
	docker compose exec api poetry run alembic upgrade head

migrate-test:
	docker compose exec api sh -lc 'DATABASE_URL="$$DATABASE_URL_TEST" poetry run alembic upgrade head'

test:
	docker compose exec api poetry run pytest -q

# -------- DUMPS --------

dump-dev:
	docker compose exec db sh -lc 'pg_dump -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -Fc -f /dumps/dev.dump'

dump-test:
	docker compose exec db pg_dump -U $${POSTGRES_USER} -d ecommerce_test -Fc -f /dumps/test.dump

# -------- RESTORE --------

restore-dev:
	docker compose exec db sh -lc 'pg_restore -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" --clean --if-exists /dumps/dev.dump'

restore-test:
	docker compose exec db pg_restore -U $${POSTGRES_USER} -d ecommerce_test --clean --if-exists /dumps/dev.dump
