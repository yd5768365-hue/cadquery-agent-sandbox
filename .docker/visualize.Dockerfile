"""
可视化服务 Dockerfile
"""

FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglu1-mesa \
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


# scripts/auto_visualize.sh
#!/bin/bash
# 自动可视化脚本

FRD_FILE=$1
OUTPUT_DIR=$2

if [ -z "$FRD_FILE" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: ./auto_visualize.sh <frd_file> <output_dir>"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# 生成应力云图
python << EOF
import sys
sys.path.append('/app')
from services.viz_service import VisualizationService

viz = VisualizationService()

# 应力云图
result = viz.visualize_stress(
    '$FRD_FILE',
    '$OUTPUT_DIR/stress.png',
    options={'colormap': 'jet', 'show_axes': True}
)

print(f"Stress visualization: {result}")

# 位移云图
result = viz.visualize_displacement(
    '$FRD_FILE',
    '$OUTPUT_DIR/displacement.png',
    scale_factor=10.0
)

print(f"Displacement visualization: {result}")

# 动画
result = viz.create_animation(
    '$FRD_FILE',
    '$OUTPUT_DIR/rotation.gif',
    num_frames=36
)

print(f"Animation: {result}")
EOF

echo "✓ Visualization complete: $OUTPUT_DIR"