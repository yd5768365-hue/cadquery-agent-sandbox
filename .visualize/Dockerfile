FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    mesa-common-dev \
    libglu1-mesa-dev \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 包
RUN pip install --no-cache-dir \
    pyvista \
    vtk \
    numpy \
    Pillow \
    imageio

WORKDIR /app

# 启动虚拟显示
ENV DISPLAY=:99

CMD ["python", "-m", "services.viz_service"]