FROM python:3.10-slim

# 配置阿里云镜像源
RUN echo "deb http://mirrors.aliyun.com/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list

# 安装系统依赖和仿真软件
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglu1-mesa libxrender1 libxext6 libxfixes3 \
    libxi6 libxcomposite1 libxcursor1 libxdamage1 libxrandr2 \
    libfontconfig1 libdbus-1-3 gmsh calculix-ccx \
    vim wget git \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 包
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    cadquery==2.4.0 \
    numpy==1.24.3 \
    scipy==1.10.1 \
    matplotlib==3.7.1 \
    meshio==5.3.4 \
    gmsh \
    pandas

#添加可视化工具
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    xvfb

RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    pyvista \
    vtk \
    Pillow
    
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

CMD ["tail", "-f", "/dev/null"]