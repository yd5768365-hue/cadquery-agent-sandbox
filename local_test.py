"""
本地运行测试脚本（不使用Docker）
"""
import subprocess
import time
from pathlib import Path

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def main():
    print("\n" + "=" * 60)
    print("CAE Platform 本地运行测试")
    print("=" * 60 + "\n")

    # 1. 检查Streamlit Dashboard
    print("1. Streamlit Dashboard:")
    print("-" * 60)
    output, code = run_cmd("curl -s http://localhost:8501 | head -5")
    if code == 0 and "Streamlit" in output:
        print("  [OK] Dashboard is running at http://localhost:8501")
    else:
        print("  [FAIL] Dashboard is not accessible")
    print()

    # 2. 测试对话记忆系统
    print("2. 对话记忆系统:")
    print("-" * 60)
    output, code = run_cmd('python conversation_memory.py <<EOF\nHello\nquit\nEOF')
    if code == 0:
        print("  [OK] 对话记忆系统正常运行")
    else:
        print("  [FAIL] 对话记忆系统失败")
    print()

    # 3. 测试记忆回顾功能
    print("3. 记忆回顾功能:")
    print("-" * 60)
    output, code = run_cmd("python scripts/memory_review_driver.py --recent 24")
    if code == 0:
        print("  [OK] 记忆回顾功能正常")
    else:
        print("  [FAIL] 记忆回顾功能失败")
    print()

    # 4. 检查Python依赖
    print("4. Python依赖:")
    print("-" * 60)
    packages = ["streamlit", "celery", "redis", "sqlalchemy", "numpy", "pandas", "sklearn"]
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"  [OK] {pkg}")
        except ImportError:
            print(f"  [FAIL] {pkg} not installed")
    print()

    # 5. 项目文件检查
    print("5. 项目文件:")
    print("-" * 60)
    files = [
        "dashboard/app.py",
        "server/server.py",
        "conversation_memory.py",
        "scripts/memory_review_driver.py",
        "conversation_history.json"
    ]
    for file in files:
        if Path(file).exists():
            print(f"  [OK] {file}")
        else:
            print(f"  [MISSING] {file}")
    print()

    print("=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n访问地址:")
    print("  Dashboard:  http://localhost:8501")
    print("  GitHub:     https://github.com/yd5768365-hue/cadquery-agent-sandbox")
    print()

if __name__ == "__main__":
    main()
