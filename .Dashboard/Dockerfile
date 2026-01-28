FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglu1 \
    libxrender1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libfontconfig1 \
    libdbus-1-3 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# 配置阿里云镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 Python 依赖
RUN pip install --no-cache-dir \
    streamlit \
    plotly \
    pandas \
    numpy \
    scipy \
    matplotlib \
    pyvista \
    vtk \
    Pillow \
    psycopg2-binary \
    redis \
    celery \
    joblib \
    scikit-learn \
    sqlalchemy \
    requests \
    python-dateutil

COPY . /app

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
