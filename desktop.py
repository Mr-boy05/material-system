"""
城治学生会物资管理系统 - 桌面版启动器
使用 PyWebView 包装网页为原生桌面应用，内嵌启动 FastAPI 后端
"""

import os
import sys
import time
import threading
import socket
import webbrowser

# 获取程序运行目录（打包后是 exe 所在目录）
def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()
os.chdir(APP_DIR)

# 确保上传目录存在
os.makedirs(os.path.join(APP_DIR, "static", "uploads"), exist_ok=True)

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

def start_server():
    """在后台线程启动 FastAPI 服务"""
    import uvicorn
    # 动态导入 main 模块
    sys.path.insert(0, APP_DIR)
    import main
    # 覆盖 main 里的端口设置
    config = uvicorn.Config(main.app, host="127.0.0.1", port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    server.run()

def wait_for_server(timeout=15):
    """等待服务启动"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect(('127.0.0.1', PORT))
                return True
        except:
            time.sleep(0.3)
    return False

def main():
    # 启动后端服务
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # 等待服务启动
    if not wait_for_server():
        # 服务启动失败，用浏览器打开
        webbrowser.open(BASE_URL)
        return

    # 启动 PyWebView 窗口
    try:
        import webview
        window = webview.create_window(
            title='城治学生会物资管理系统',
            url=BASE_URL,
            width=1280,
            height=800,
            min_size=(900, 600),
            resizable=True,
            text_select=True
        )
        webview.start(debug=False)
    except ImportError:
        # 没有安装 pywebview，用浏览器打开
        webbrowser.open(BASE_URL)
        input("按回车键退出...")

if __name__ == "__main__":
    main()
