#!/usr/bin/env python3
"""
A股价值分析器启动脚本
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 启动 A股价值分析器...")
    
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查虚拟环境
    venv_path = os.path.join(current_dir, ".venv")
    if not os.path.exists(venv_path):
        print("❌ 虚拟环境不存在，请先创建虚拟环境")
        return
    
    # 检查应用文件
    app_path = os.path.join(current_dir, "apps", "streamlit_app.py")
    if not os.path.exists(app_path):
        print("❌ 应用文件不存在")
        return
    
    print("✅ 环境检查通过")
    print(f"📁 项目目录: {current_dir}")
    print(f"🔧 应用文件: {app_path}")
    
    # 启动 Streamlit 应用
    try:
        print("\n🌐 正在启动 Streamlit 应用...")
        print("📱 应用将在浏览器中打开: http://localhost:8501")
        print("⏹️  按 Ctrl+C 停止应用")
        print("-" * 50)
        
        # 启动命令
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            app_path, 
            "--server.port", "8501",
            "--server.headless", "true"
        ]
        
        # 设置环境变量
        env = os.environ.copy()
        env["PYTHONPATH"] = current_dir + ":" + env.get("PYTHONPATH", "")
        
        # 启动进程
        process = subprocess.Popen(cmd, env=env, cwd=current_dir)
        
        # 等待用户中断
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止应用...")
            process.terminate()
            process.wait()
            print("✅ 应用已停止")
    
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()
