FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
ENV PYTHONPATH=/app/src:$PYTHONPATH
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN mkdir -p results/figures results/tables data/raw data/processed
CMD ["bash", "-c", "pytest -q && python scripts/run_all.py"]
