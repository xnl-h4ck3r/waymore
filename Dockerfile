FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential ca-certificates curl git && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && test -f requirements.txt && pip install -r requirements.txt
COPY . .
RUN pip install .

FROM base AS runtime
RUN useradd -ms /bin/bash appuser
USER appuser
WORKDIR /app
RUN mkdir -p results
ENTRYPOINT ["waymore"]
