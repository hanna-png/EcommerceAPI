# Ecommerce API

Backend API for an e-commerce system built with FastAPI and PostgreSQL.
The project is fully dockerized and includes database migrations and integration tests.

# Tech stack
1. FastAPI
2. Postgres
3. SQLAlchemy
4. Docker
5. GitHub
6. ruff linter
7. FactoryBoy - Faker

# Setup
Clone the repository and create an environment file:

```bash
cp .env.example .env
```

Build and start the project:
```bash
make build
```

Run database migrations:
```bash
make migrate
make migrate-test
```

API will be available at:

http://localhost:8000

Swagger docs: http://localhost:8000/docs

# Run tests
```bash
make test
```
