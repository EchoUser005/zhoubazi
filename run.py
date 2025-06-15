import subprocess
import threading
import time
import os
import sys
import webbrowser

# 添加当前目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def run_backend():
    """运行FastAPI后端服务"""
    print("启动后端API服务...")
    subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])

def run_frontend():
    """运行Streamlit前端服务"""
    print("启动前端服务...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py", 
        "--server.port", "8501", 
        "--server.headless", "true",
        "--browser.serverAddress", "localhost"
    ])

def main():
    """主函数，启动所有服务"""
    print("\n" + "="*50)
    print("周运势分析系统启动中...")
    print("="*50 + "\n")
    
    # 启动后端线程
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # 启动前端线程
    frontend_thread = threading.Thread(target=run_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # 等待服务启动
    print("等待服务启动，请稍候...")
    time.sleep(5)  # 等待5秒，确保服务都已启动
    
    # 打开浏览器
    print("正在打开浏览器访问前端页面...")
    webbrowser.open("http://localhost:8501")
    
    # 保持主线程存活，以便daemon线程可以继续运行
    print("\n" + "="*50)
    print("系统已启动。后台服务正在运行中。")
    print("如果浏览器没有自动打开，请手动访问 http://localhost:8501")
    print("如需停止服务，请在本窗口按 Ctrl+C。")
    print("="*50 + "\n")
    
    try:
        # 让主线程等待，直到接收到Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n收到退出指令，正在关闭服务...")
        print("服务已停止。")

if __name__ == "__main__":
    main() 