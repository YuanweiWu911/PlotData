import sys
import logging
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QDir

from core.data_manager import DataManager
from core.visualization import Visualizer
from core.config_manager import ConfigManager
from ui.main_window import MainWindow

def setup_logging():
    """设置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("plotdata.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("PlotData")

def main():
    # 设置日志
    logger = setup_logging()
    logger.info("启动应用程序")
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("PlotData")
    
    # 设置应用程序图标
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 设置应用程序样式
    theme = config_manager.get("theme", "light")
    if theme == "dark":
        # 应用深色主题
        app.setStyle("Fusion")
        # 这里可以添加深色主题的调色板设置
    else:
        app.setStyle("Fusion")
    
    # 创建数据管理器和可视化器
    data_manager = DataManager()
    visualizer = Visualizer()
    
    # 创建主窗口
    window = MainWindow(data_manager, visualizer, config_manager)
    
    # 恢复窗口大小和位置
    window_size = config_manager.get("window_size", [800, 600])
    window_position = config_manager.get("window_position", [100, 100])
    window.resize(window_size[0], window_size[1])
    window.move(window_position[0], window_position[1])
    
    window.show()
    
    logger.info("应用程序界面已加载")
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    # 在Windows上设置应用程序ID（在创建QApplication后）
    if os.name == 'nt':
        import ctypes
        app_id = 'yuanweiwu911.plotdata.1.0'  # 应用程序ID格式：公司名.产品名.版本
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    import sys
    sys.setrecursionlimit(3000)  # 默认是1000，增加到3000
    main()