"""
城治学生会物资管理系统 - 桌面版启动器
启动本地后端服务，自动打开浏览器访问
"""

import os
import sys
import time
import threading
import socket
import webbrowser
import traceback

# 获取程序运行目录
def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()
os.chdir(APP_DIR)

# 日志输出到文件
LOG_FILE = os.path.join(APP_DIR, "desktop.log")
def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except:
        pass

log("=" * 50)
log("桌面版启动")
log(f"工作目录: {APP_DIR}")

# 确保目录存在
os.makedirs(os.path.join(APP_DIR, "static", "uploads"), exist_ok=True)
os.makedirs(os.path.join(APP_DIR, "data"), exist_ok=True)

# 检查端口是否被占用
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

# 找到可用端口
def find_available_port(start=8000):
    port = start
    while is_port_in_use(port):
        port += 1
    return port

PORT = find_available_port()
BASE_URL = f"http://127.0.0.1:{PORT}"
log(f"使用端口: {PORT}")

server_started = threading.Event()

def start_server():
    """在后台线程启动 FastAPI 服务"""
    try:
        log("开始启动后端服务...")
        # 修复无控制台模式下 stdout 为 None
        if sys.stdout is None:
            sys.stdout = open(os.path.join(APP_DIR, "server_stdout.log"), "w", encoding="utf-8")
        if sys.stderr is None:
            sys.stderr = open(os.path.join(APP_DIR, "server_stderr.log"), "w", encoding="utf-8")

        import uvicorn
        sys.path.insert(0, APP_DIR)
        import main
        log("main 模块导入成功")
        config = uvicorn.Config(main.app, host="127.0.0.1", port=PORT, log_level="warning", log_config=None)
        server = uvicorn.Server(config)
        log("uvicorn 配置完成，开始运行")
        server_started.set()
        server.run()
    except Exception as e:
        log(f"后端服务启动失败: {e}")
        log(traceback.format_exc())
        server_started.set()

def wait_for_server(timeout=20):
    """等待服务启动"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect(('127.0.0.1', PORT))
                log("服务启动成功，端口可连接")
                return True
        except:
            time.sleep(0.3)
    log("等待服务启动超时")
    return False

def main():
    try:
        # 启动后端服务
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        log("后端线程已启动")

        # 等待服务启动
        if not wait_for_server():
            log("服务启动失败")
            input("服务启动失败，按回车键退出...")
            return

        # 打开浏览器
        log(f"打开浏览器: {BASE_URL}")
        webbrowser.open(BASE_URL)

        # 保持进程运行
        print("=" * 50)
        print("  城治学生会物资管理系统 已启动")
        print(f"  访问地址: {BASE_URL}")
        print("  浏览器已自动打开，关闭此窗口即可退出程序")
        print("=" * 50)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log("用户中断退出")

    except KeyboardInterrupt:
        log("用户中断退出")
    except Exception as e:
        log(f"主程序异常: {e}")
        log(traceback.format_exc())

if __name__ == "__main__":
    main()
