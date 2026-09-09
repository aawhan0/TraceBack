FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRACEBACK_ENVIRONMENT=production \
    TRACEBACK_DATABASE_PATH=/data/traceback.db

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app

RUN python -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . \
    && python -m pip install --no-cache-dir --upgrade --force-reinstall "setuptools>=78.1.1" "msgpack>=1.2.1,<2"

RUN useradd --create-home --uid 10001 traceback \
    && mkdir -p /data \
    && chown -R traceback:traceback /app /data

USER traceback

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
