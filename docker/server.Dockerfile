FROM python:3.10-slim

WORKDIR /app

# 安装依赖
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 包
RUN pip install --no-cache-dir \
    celery[redis]==5.3.4 \
    flower==2.0.1 \
    psycopg2-binary==2.9.9 \
    sqlalchemy==2.0.23 \
    numpy==1.26.2 \
    pandas==2.1.4 \
    redis==5.0.1

COPY . /app

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
