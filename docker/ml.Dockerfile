FROM python:3.10

# 安装 PyTorch 和 ML 库
RUN pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    scikit-learn \
    joblib \
    faiss-cpu \
    numpy \
    pandas

# 可选：如果有 GPU
# RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

WORKDIR /app

CMD ["tail", "-f", "/dev/null"]
