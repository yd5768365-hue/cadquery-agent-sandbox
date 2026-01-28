FROM python:3.10-slim

WORKDIR /app

# 安装依赖
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 包
RUN pip install --no-cache-dir \
    celery[redis] \
    flower \
    psycopg2-binary \
    sqlalchemy \
    numpy \
    pandas

COPY . /app

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
