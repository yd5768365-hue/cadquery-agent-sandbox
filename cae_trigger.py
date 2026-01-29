#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAE智能体触发器
当用户输入"cae"时，自动激活CAE项目智能体
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def activate_cae_agent():
    """激活CAE项目智能体"""
    memory_file = PROJECT_ROOT / "cae_agent_memory.md"
    
    if memory_file.exists():
        print("正在激活CAE数字孪生项目智能体...")
        print("=" * 50)
        
        # 读取记忆文件内容
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory_content = f.read()
        
        # 提取智能体信息
        agent_info = []
        in_agent_info = False
        
        for line in memory_content.split('\n'):
            if line.startswith('## 智能体信息'):
                in_agent_info = True
            elif line.startswith('## ') and in_agent_info:
                break
            elif in_agent_info:
                agent_info.append(line)
        
        print('\n'.join(agent_info))
        print("=" * 50)
        print("CAE智能体已激活！现在可以开始对话了。")
        print("\n您可以询问以下类型的问题：")
        print("   - 项目功能改进建议")
        print("   - 学习规划和资源推荐")
        print("   - CAE理论知识解答")
        print("   - 代码实现和调试帮助")
        print("   - 仿真分析技术支持")
        
        return True
    else:
        print("❌ 未找到CAE智能体记忆文件")
        return False

if __name__ == "__main__":
    # 检查是否通过"cae"命令触发
    if len(sys.argv) > 1 and sys.argv[1].lower() == "cae":
        activate_cae_agent()
    else:
        print("使用方法: python cae_trigger.py cae")