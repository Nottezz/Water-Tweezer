FROM python:3.14-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:0.9.29 /uv /uvx /bin/

WORKDIR /app

COPY ./pyproject.toml ./
COPY ./uv.lock ./
COPY config.default.yaml ./
COPY ./alembic ./alembic
COPY ./alembic.ini ./alembic.ini
COPY ./water_tweezer ./water_tweezer

RUN uv sync --locked --no-dev

CMD ["sh", "-c", "uv run alembic upgrade head && uv run python -m water_tweezer.water_bot.main"]
