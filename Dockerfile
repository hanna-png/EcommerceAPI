FROM python:3.13-slim
WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* README.md /app/

RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root


COPY . /app

EXPOSE 8000
