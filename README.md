## 渲染预览

下面是一个占位渲染图（占位图仅用于展示布局，建议替换为你本地生成的模型截图）：

![CadQuery 渲染预览 (占位)](https://via.placeholder.com/640x360.png?text=CadQuery+Preview)

说明：
- 如果你有实际截图，请把图片上传到仓库（例如 images/preview.png）或提供外部链接，我会把占位图替换为真实图像并更新 README。  
- 也可以让我生成一张示意图或 SVG 占位图并提交（非真实模型渲染，仅视觉占位）。

## 依赖与标准零件库

- 本项目已集成 cq_warehouse 标准零件库，包含常用标准件与参数化零件，且该库在项目的容器镜像中已预装，随容器环境一起可用。若在其他环境中运行，请按 cq_warehouse 官方方式安装。  
- 容器内的验证工具（CQ 检测库）：项目容器中集成了标准的 CadQuery 验证/检测库（CQ 检测库），用于自动校验生成几何与参数，Agent 会在生成后调用该库进行自动验证并依据结果决定是否进入修复循环。

容器内示例流程（高层）：
1. 启动并进入容器：`docker exec -it <container-name> /bin/bash`  
2. 运行示例并触发验证：`python examples/bolt_example.py && python tools/validate_cq.py examples/bolt_example.py`  
3. 验证结果会以日志/报告输出，Agent 会据此执行后续步骤。