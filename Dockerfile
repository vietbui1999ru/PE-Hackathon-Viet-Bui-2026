FROM python:3.13
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY . .
RUN uv sync
CMD ["uv", "run", "run.py"]
