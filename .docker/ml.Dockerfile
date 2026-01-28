FROM python:3.10

# 配置镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 PyTorch (CPU版本)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 安装其他 ML 库
RUN pip install --no-cache-dir \
    scikit-learn \
    joblib \
    faiss-cpu \
    numpy \
    pandas

# 可选：如果有 GPU
# RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

WORKDIR /app

CMD ["tail", "-f", "/dev/null"]
