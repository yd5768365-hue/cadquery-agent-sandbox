FROM python:3.10-slim

# 配置阿里云镜像
RUN echo "deb http://mirrors.aliyun.com/debian/ bookworm main contrib non-free" > /etc/apt/sources.list

# 安装 CalculiX
RUN apt-get update && apt-get install -y \
    calculix-ccx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV OMP_NUM_THREADS=8

CMD ["tail", "-f", "/dev/null"]
