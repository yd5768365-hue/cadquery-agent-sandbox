FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    streamlit \
    plotly \
    pandas \
    numpy \
    psycopg2-binary \
    redis

COPY . /app

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]