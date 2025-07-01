import subprocess
import sys
import os
import time

def check_and_install_frontend_deps():
    """Checks if node_modules exists in the app directory and runs 'npm install' if not."""
    app_dir = os.path.join(os.path.dirname(__file__), 'app')
    node_modules_path = os.path.join(app_dir, 'node_modules')
    
    if not os.path.exists(node_modules_path):
        print("--- 前端依赖 'node_modules' 不存在，正在执行 'npm install'... ---")
        try:
            # 使用 shell=True 来正确处理 Windows 上的 npm.cmd
            npm_install_process = subprocess.Popen('npm install', cwd=app_dir, shell=True)
            npm_install_process.wait() # 等待安装完成
            if npm_install_process.returncode == 0:
                print("--- 前端依赖安装成功 ---")
            else:
                print(f"--- 前端依赖安装失败，返回码: {npm_install_process.returncode} ---")
                sys.exit(1)
        except Exception as e:
            print(f"--- 执行 'npm install' 时出错: {e} ---")
            sys.exit(1)
    else:
        print("--- 前端依赖 'node_modules' 已存在，跳过安装 ---")

def run():
    """
    Runs both the FastAPI backend and the Next.js frontend concurrently.
    """
    backend_command = [sys.executable, "main.py"]
    frontend_command = "npm run dev"

    app_dir = os.path.join(os.path.dirname(__file__), 'app')

    backend_process = None
    frontend_process = None

    try:
        print("--- 正在启动 FastAPI 后端服务... ---")
        # 使用 subprocess.PIPE 来捕获输出
        backend_process = subprocess.Popen(
            backend_command, 
            stdout=sys.stdout, 
            stderr=sys.stderr,
            cwd=os.path.dirname(__file__)
        )
        print(f"--- 后端服务已启动，进程 PID: {backend_process.pid} ---")
        
        # 给予后端一些启动时间
        time.sleep(3)

        print("--- 正在启动 Next.js 前端开发服务... ---")
        # 对于npm命令，在Windows上使用shell=True是更可靠的方式
        frontend_process = subprocess.Popen(
            frontend_command, 
            stdout=sys.stdout, 
            stderr=sys.stderr,
            cwd=app_dir, 
            shell=True
        )
        print(f"--- 前端服务已启动，进程 PID: {frontend_process.pid} ---")

        # 等待任一进程结束
        while backend_process.poll() is None and frontend_process.poll() is None:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n--- 收到退出信号 (Ctrl+C)，正在关闭所有服务... ---")
    
    except Exception as e:
        print(f"\n--- 发生错误: {e} ---")

    finally:
        if frontend_process and frontend_process.poll() is None:
            print("--- 正在终止前端服务... ---")
            # 在Windows上，需要用 taskkill 来终止 shell 启动的进程树
            if sys.platform == "win32":
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(frontend_process.pid)])
            else:
                frontend_process.terminate()
            frontend_process.wait()
            print("--- 前端服务已关闭 ---")
        
        if backend_process and backend_process.poll() is None:
            print("--- 正在终止后端服务... ---")
            backend_process.terminate()
            backend_process.wait()
            print("--- 后端服务已关闭 ---")

        print("\n--- 所有服务已成功关闭 ---")


if __name__ == "__main__":
    check_and_install_frontend_deps()
    run() 