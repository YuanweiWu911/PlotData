import os
from PyQt6 import sip  # 新增导入
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QFileDialog, QMessageBox, QToolBar, 
                            QStatusBar, QLabel, QDialog, QApplication, 
                            QPushButton, QGroupBox, QInputDialog)
from PyQt6.QtCore import Qt, QSize  # 添加 QSize 导入
from PyQt6.QtGui import QIcon, QPalette, QColor, QAction  # 从 QtGui 导入 QAction
from .plot_view import PlotView
from core.config_manager import ConfigManager
from core.data_manager import DataManager
from core import visualization
from ui.data_view import DataView
from ui.plot_view import PlotView
from ui.stats_view import StatsView

class MainWindow(QMainWindow):
    def __init__(self, data_manager, visualizer, config_manager=None):
        super().__init__()
        
        self.data_manager = data_manager
        self.visualizer = visualizer
        self.config_manager = config_manager
        
        # 初始化UI
        self.init_ui()
        
        # 设置窗口标题
        self.setWindowTitle("PlotData - 数据可视化工具")
         
    def init_ui(self):
        """初始化用户界面"""
        # 创建操作
        self.create_actions()
        
        # 创建菜单
        self.create_menu()
        
        # 创建工具栏
#       self.create_toolbar()
        
        # 创建状态栏
        self.create_statusbar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建左侧工具栏并添加到主布局
        left_toolbar_layout = self.create_left_toolbar()
        if left_toolbar_layout:
            main_layout.addLayout(left_toolbar_layout)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建数据视图
        self.data_view = DataView(self.data_manager)
        splitter.addWidget(self.data_view)
        
        # 创建绘图视图
        self.plot_view = PlotView(self.data_manager, self.visualizer)
        splitter.addWidget(self.plot_view)
        
        # 设置分割器初始大小
        splitter.setSizes([400, 600])
        
        # 添加分割器到主布局
        main_layout.addWidget(splitter)

        # 在UI初始化完成后调用一次切换函数，确保初始状态正确
        # 现在可以安全调用，因为按钮已经创建
        if hasattr(self, 'preview_toggle_button'):
            self.toggle_data_preview()

        # 设置窗口大小
        if self.config_manager:
            window_size = self.config_manager.get("window_size", [800, 600])
            self.resize(window_size[0], window_size[1])
            window_position = self.config_manager.get("window_position", [100, 100])
            self.move(window_position[0], window_position[1])
        else:
            self.resize(1000, 700)

        # 修正信号连接，确保接收所有11个参数
        self.data_view.plot_requested.connect(
            lambda p,x,y,c,xe,ye,ms,msz,ht,b,cm: 
            self.plot_view.handle_plot_request(
                p,x,y,c,xe,ye,ms,msz,ht,b,cm
            )
        )

    def create_actions(self):
        # 文件操作
        self.open_action = QAction("载入数据", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(lambda: self.open_file())  # 确保使用lambda传递空参数
        
        # 添加导出功能
        self.export_action = QAction("导出数据", self)
        self.export_action.setShortcut("Ctrl+E")
        self.export_action.triggered.connect(self.export_data)
        
        self.exit_action = QAction("退出", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        
        # 帮助操作
        self.about_action = QAction("关于", self)
        self.about_action.triggered.connect(self.show_about)
        
        # 添加主题切换功能
        self.toggle_theme_action = QAction("切换深色/浅色主题", self)
        self.toggle_theme_action.setShortcut("Ctrl+T")
        self.toggle_theme_action.triggered.connect(self.toggle_theme)
        
        # 添加数据清洗操作
        self.clean_data_action = QAction("数据清洗", self)
        self.clean_data_action.triggered.connect(self.show_clean_dialog)
        
        # 添加帮助操作
        self.help_action = QAction("帮助内容", self)
        self.help_action.setShortcut("F1")
        self.help_action.triggered.connect(self.show_help)
        
        # 添加首选项操作
        self.preferences_action = QAction("首选项", self)
        self.preferences_action.setShortcut("Ctrl+P")
        self.preferences_action.triggered.connect(self.show_preferences)
        
        # 创建最近文件操作
        self.recent_file_actions = []
        for i in range(10):  # 最多显示10个最近文件
            action = QAction(self)
            action.setVisible(False)
            action.triggered.connect(self.open_recent_file)
            self.recent_file_actions.append(action)

                # 添加保存图表操作
            self.save_plot_action = QAction("保存图表", self)
            self.save_plot_action.setShortcut("Ctrl+S")
            self.save_plot_action.triggered.connect(self.save_current_plot)

    def create_menu(self):
        # 创建菜单栏
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        file_menu.addAction(self.open_action)
        
        # 添加最近文件子菜单
        self.recent_menu = file_menu.addMenu("最近打开的文件")
        for action in self.recent_file_actions:
            self.recent_menu.addAction(action)
        
        self.update_recent_file_actions()
        
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        edit_menu.addAction(self.preferences_action)
        
        # 添加数据菜单
        data_menu = menu_bar.addMenu("数据")
        data_menu.addAction(self.clean_data_action)
        
        # 添加视图菜单
        view_menu = menu_bar.addMenu("视图")
        view_menu.addAction(self.toggle_theme_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        help_menu.addAction(self.help_action)
        help_menu.addAction(self.about_action)
        
#   def create_toolbar(self):
#       # 创建工具栏
#       toolbar = QToolBar("主工具栏")
#       toolbar.setIconSize(QSize(16, 16))
#       self.addToolBar(toolbar)
#       
#       toolbar.addAction(self.open_action)
#       toolbar.addAction(self.export_action)
#       toolbar.addAction(self.save_plot_action)  

    def save_current_plot(self):
        """保存当前图表"""
        if hasattr(self, 'plot_view') and self.plot_view:
            self.plot_view.save_plot()

    def create_statusbar(self):
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)

    def update_recent_file_actions(self):
        """更新最近文件操作"""
        if self.config_manager is None:
            self.recent_menu.setEnabled(False)
            return
        
        recent_files = self.config_manager.get("recent_files", [])
        
        num_recent_files = min(len(recent_files), len(self.recent_file_actions))
        
        for i in range(num_recent_files):
            file_path = recent_files[i]
            file_name = os.path.basename(file_path)
            text = f"&{i+1} {file_name}"
            
            self.recent_file_actions[i].setText(text)
            self.recent_file_actions[i].setData(file_path)
            self.recent_file_actions[i].setVisible(True)
        
        for i in range(num_recent_files, len(self.recent_file_actions)):
            self.recent_file_actions[i].setVisible(False)
        
        self.recent_menu.setEnabled(num_recent_files > 0)

    def open_file(self, file_path=None):
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "打开数据文件", 
                "", 
                "文本文件 (*.txt);;CSV文件 (*.csv);;Excel文件 (*.xlsx *.xls);;JSON文件 (*.json);;所有文件 (*.*)"
            )
        
        if file_path:
            try:
                # 修正类名拼写（注意Q大写）
                sep, ok = QInputDialog.getText(  # 修正为QInputDialog
                    self,
                    "分隔符设置",
                    "请输入列分隔符（留空使用默认）:", 
                    text=","
                )
                sep = sep.strip() if sep.strip() else None
                
                # 加载数据前检查视图对象
                if not sip.isdeleted(self.data_view):
                    # 修改加载方法调用，添加分隔符参数
                    success, message = self.data_manager.load_data(file_path, sep=sep)
                    
                    if success:
                        # 更新数据视图
                        self.data_view.update_data_view()
                        
                        # 更新状态栏
                        file_info = self.data_manager.get_file_info()
                        if file_info:
                            self.status_label.setText(
                                f"当前文件: {file_info['file_name']} | "
                                f"行数: {file_info['rows']} | "
                                f"列数: {file_info['columns']}"
                            )
                        
                        # 添加到最近文件列表
                        if self.config_manager is not None:
                            self.config_manager.add_recent_file(file_path)
                            self.update_recent_file_actions()
                        
                        QMessageBox.information(self, "成功", message)
                    else:
                        QMessageBox.critical(self, "错误", message)
                else:
                    QMessageBox.critical(self, "错误", "视图组件已失效，请重启应用")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载文件失败: {str(e)}")
        else:
            QMessageBox.information(self, "提示", "已取消文件选择")

    def open_recent_file(self):
        """打开最近文件"""
        action = self.sender()
        if action:
            file_path = action.data()
            if file_path and os.path.exists(file_path):
                self.open_file(file_path)
            else:
                QMessageBox.warning(self, "警告", f"文件不存在: {file_path}")
                
                # 从最近文件列表中移除
                if self.config_manager is not None:
                    recent_files = self.config_manager.get("recent_files", [])
                    if file_path in recent_files:
                        recent_files.remove(file_path)
                        self.config_manager.set("recent_files", recent_files)
                        self.update_recent_file_actions()

    def clear_recent_files(self):
        """清除最近文件列表"""
        if self.config_manager is not None:
            self.config_manager.set("recent_files", [])
            self.update_recent_file_actions()
            QMessageBox.information(self, "成功", "已清除最近文件列表")

    def export_data(self):
        """导出当前数据"""
        if self.data_manager.get_data() is None:
            QMessageBox.warning(self, "警告", "没有可导出的数据")
            return
        
        # 打开文件保存对话框
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "导出数据", "", 
            "CSV文件 (*.csv);;Excel文件 (*.xlsx);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # 根据选择的文件类型导出数据
            if file_path.endswith('.csv'):
                self.data_manager.get_data().to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                self.data_manager.get_data().to_excel(file_path, index=False)
            elif file_path.endswith('.json'):
                self.data_manager.get_data().to_json(file_path, orient='records')
            else:
                # 默认导出为CSV
                if not file_path.endswith('.csv'):
                    file_path += '.csv'
                self.data_manager.get_data().to_csv(file_path, index=False)
            
            self.status_label.setText(f"数据已导出至: {file_path}")
            QMessageBox.information(self, "成功", f"数据已成功导出至: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出数据失败: {str(e)}")

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 PlotData",
            """<b>PlotData</b> v1.0
            <p>一款基于Python的交互式数据可视化工具。</p>
            <p>使用 PyQt6, Matplotlib, NumPy 和 Pandas 开发。</p>
            """
        )

    def toggle_theme(self):
        """切换深色/浅色主题"""
        app = QApplication.instance()
        
        # 检查当前主题
        if app.style().objectName() == "fusion":
            # 如果当前是深色主题，切换到默认主题
            app.setStyle("windowsvista")
            app.setPalette(app.style().standardPalette())
            self.status_label.setText("已切换到浅色主题")
        else:
            # 切换到深色主题
            app.setStyle("fusion")
            
            # 设置深色主题调色板
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
            
            app.setPalette(dark_palette)
            
            self.status_label.setText("已切换到深色主题")

    def show_clean_dialog(self):
        """显示数据清洗对话框"""
        if self.data_manager.get_data() is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        from ui.clean_dialog import DataCleanDialog
        dialog = DataCleanDialog(self.data_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 更新数据视图
            self.data_view.update_data_view()
            # 更新状态栏
            file_info = self.data_manager.get_file_info()
            if file_info:
                self.status_label.setText(
                    f"当前文件: {file_info['file_name']} | "
                    f"行数: {file_info['rows']} | "
                    f"列数: {file_info['columns']}"
                )

    def show_preferences(self):
        """显示首选项对话框"""
        if self.config_manager is None:
            QMessageBox.warning(self, "警告", "配置管理器未初始化")
            return
        
        from ui.preferences_dialog import PreferencesDialog
        dialog = PreferencesDialog(self.config_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 应用主题变更
            theme = self.config_manager.get("theme", "light")
            if theme == "dark":
                self.apply_dark_theme()
            else:
                self.apply_light_theme()

    def apply_dark_theme(self):
        """应用深色主题"""
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        # 设置深色主题调色板
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        app.setPalette(dark_palette)
        
        self.status_label.setText("已应用深色主题")

    def apply_light_theme(self):
        """应用浅色主题"""
        app = QApplication.instance()
        app.setStyle("Fusion")
        app.setPalette(app.style().standardPalette())
        
        self.status_label.setText("已应用浅色主题")

    def show_help(self):
        """显示帮助对话框"""
        from ui.help_dialog import HelpDialog
        dialog = HelpDialog(self)
        dialog.exec()

    def create_left_toolbar(self):
        """创建左侧工具栏"""
        left_toolbar = QHBoxLayout()
        
#       # 导入数据按钮
#       self.import_button = QPushButton("导入数据")
#       self.import_button.clicked.connect(self.open_file)  # 修正为正确的方法名
#       left_toolbar.addWidget(self.import_button)
        
        # 添加数据预览切换按钮
        self.preview_toggle_button = QPushButton("数据预览")
        self.preview_toggle_button.setCheckable(True)  # 设置为可切换状态
        self.preview_toggle_button.setChecked(True)    # 默认为显示状态
        self.preview_toggle_button.clicked.connect(self.toggle_data_preview)
        left_toolbar.addWidget(self.preview_toggle_button)
        
        # 返回布局以便添加到主布局
        return left_toolbar

    def toggle_data_preview(self):
        """切换数据预览和筛选区域的显示状态"""
        # 确保按钮已创建
        if not hasattr(self, 'preview_toggle_button'):
            return
            
        is_visible = self.preview_toggle_button.isChecked()
        
        # 获取数据视图中的相关控件
        if hasattr(self, 'data_view'):
            # 获取数据表格视图
            if hasattr(self.data_view, 'table_view'):
                self.data_view.table_view.setVisible(is_visible)
                
            # 获取数据筛选区域 - 根据data_view.py中的实际代码
            filter_group = None
            for child in self.data_view.children():
                if isinstance(child, QGroupBox) and child.title() == "数据筛选":
                    filter_group = child
                    break
                    
            if filter_group:
                filter_group.setVisible(is_visible)
        
        # 更新按钮文本，提供更好的用户反馈
        self.preview_toggle_button.setText("数据预览 ✓" if is_visible else "数据预览")

    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.config_manager is not None:
            # 保存窗口大小和位置
            self.config_manager.set("window_size", [self.width(), self.height()])
            self.config_manager.set("window_position", [self.x(), self.y()])
            self.config_manager.save_config()
        
        event.accept()