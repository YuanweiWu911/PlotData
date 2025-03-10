from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QGroupBox, QFormLayout, QLineEdit,
                            QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage

import matplotlib
matplotlib.use('QtAgg')

# 添加缺失的导入
from visualization import Visualizer

class PlotView(QWidget):
    """绘图视图组件"""
    
    def __init__(self, data_manager, visualizer):
        super().__init__()
        
        self.data_manager = data_manager
        self.visualizer = visualizer
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建绘图区域
        plot_group = QGroupBox("绘图区域")
        plot_layout = QVBoxLayout(plot_group)
        
        # 创建画布
        from visualization import PlotCanvas
        self.canvas = PlotCanvas(self, width=5, height=4)
        plot_layout.addWidget(self.canvas)
        
        # 设置可视化器的画布
        self.visualizer.set_canvas(self.canvas)
        
        main_layout.addWidget(plot_group)
        
        # 创建图表设置区域
        settings_group = QGroupBox("图表设置")
        settings_layout = QFormLayout(settings_group)
        
        # 标题设置
        self.title_edit = QLineEdit()
        settings_layout.addRow("标题:", self.title_edit)
        
        # X轴标签设置
        self.x_label_edit = QLineEdit()
        settings_layout.addRow("X轴标签:", self.x_label_edit)
        
        # Y轴标签设置
        self.y_label_edit = QLineEdit()
        settings_layout.addRow("Y轴标签:", self.y_label_edit)
        
        # 应用设置按钮
        self.apply_settings_button = QPushButton("应用设置")
        self.apply_settings_button.clicked.connect(self.apply_settings)
        settings_layout.addRow("", self.apply_settings_button)
        
        # 添加保存/加载设置按钮
        settings_buttons_layout = QHBoxLayout()
        
        self.save_settings_button = QPushButton("保存设置")
        self.save_settings_button.clicked.connect(self.save_plot_settings)
        settings_buttons_layout.addWidget(self.save_settings_button)
        
        self.load_settings_button = QPushButton("加载设置")
        self.load_settings_button.clicked.connect(self.load_plot_settings)
        settings_buttons_layout.addWidget(self.load_settings_button)
        
        settings_layout.addRow("", settings_buttons_layout)
        
        main_layout.addWidget(settings_group)
        
        # 创建保存图表区域
        save_group = QGroupBox("保存图表")
        save_layout = QHBoxLayout(save_group)
        
        # 保存按钮
        self.save_button = QPushButton("保存图表")
        self.save_button.clicked.connect(self.save_plot)
        save_layout.addWidget(self.save_button)
        
        main_layout.addWidget(save_group)
        
        # 存储当前绘图参数
        self.current_plot_params = None
    
    @pyqtSlot(dict)
    def handle_plot_request(self, plot_params):
        """处理绘图请求"""
        self.current_plot_params = plot_params
        
        plot_type = plot_params["plot_type"]
        data = plot_params["data"]
        x_col = plot_params["x_col"]
        color = plot_params["color"]
        
        # 根据绘图类型调用不同的绘图方法
        if plot_type == "散点图":
            y_col = plot_params["y_col"]
            success, message = self.visualizer.scatter_plot(
                data, x_col, y_col, color=color
            )
            
        elif plot_type == "带误差棒的散点图":
            y_col = plot_params["y_col"]
            xerr_col = plot_params.get("xerr_col")
            yerr_col = plot_params.get("yerr_col")
            success, message = self.visualizer.scatter_plot_with_error(
                data, x_col, y_col, xerr_col, yerr_col, color=color
            )
            
        elif plot_type == "直方图":
            bins = plot_params["bins"]
            success, message = self.visualizer.histogram(
                data, x_col, bins=bins, color=color
            )
            
        elif plot_type == "2D密度图":
            y_col = plot_params["y_col"]
            bins = plot_params["bins"]
            success, message = self.visualizer.density_map_2d(
                data, x_col, y_col, bins=bins
            )
        
        else:
            success = False
            message = f"未知的绘图类型: {plot_type}"
        
        # 显示结果消息
        if not success:
            QMessageBox.warning(self, "绘图错误", message)
    
    def apply_settings(self):
        """应用图表设置"""
        if self.current_plot_params is None:
            QMessageBox.information(self, "提示", "请先绘制图表")
            return
        
        # 获取设置
        title = self.title_edit.text()
        x_label = self.x_label_edit.text()
        y_label = self.y_label_edit.text()
        
        # 重新绘制图表
        plot_params = self.current_plot_params.copy()
        
        # 添加设置参数
        if title:
            plot_params["title"] = title
        if x_label:
            plot_params["x_label"] = x_label
        if y_label:
            plot_params["y_label"] = y_label
        
        # 重新调用绘图处理函数
        self.handle_plot_request(plot_params)
    
    def save_plot(self):
        """保存当前图表"""
        if self.canvas is None or self.current_plot_params is None:
            QMessageBox.information(self, "提示", "没有可保存的图表")
            return
        
        # 打开文件保存对话框
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "保存图表", "", 
            "PNG图片 (*.png);;JPEG图片 (*.jpg);;PDF文档 (*.pdf);;SVG图片 (*.svg);;EPS图片 (*.eps)"
        )
        
        if not file_path:
            return
        
        try:
            # 根据文件扩展名设置DPI和其他参数
            dpi = 300  # 默认DPI
            
            # 显示保存进度对话框
            progress_dialog = QProgressDialog("正在保存图表...", "取消", 0, 100, self)
            progress_dialog.setWindowTitle("保存进度")
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.setValue(10)
            
            # 根据文件类型设置特定参数
            if file_path.endswith('.pdf'):
                # PDF需要特殊处理以确保文本可搜索
                self.canvas.fig.savefig(file_path, dpi=dpi, format='pdf', bbox_inches='tight')
            elif file_path.endswith('.svg'):
                # SVG是矢量格式
                self.canvas.fig.savefig(file_path, format='svg', bbox_inches='tight')
            elif file_path.endswith('.eps'):
                # EPS也是矢量格式
                self.canvas.fig.savefig(file_path, format='eps', bbox_inches='tight')
            else:
                # 位图格式(PNG, JPG等)
                if file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                    self.canvas.fig.savefig(file_path, dpi=dpi, format='jpeg', 
                                          bbox_inches='tight', quality=95)
                else:
                    # 默认使用PNG
                    if not (file_path.endswith('.png')):
                        file_path += '.png'
                    self.canvas.fig.savefig(file_path, dpi=dpi, format='png', 
                                          bbox_inches='tight')
            
            progress_dialog.setValue(100)
            QMessageBox.information(self, "成功", f"图表已保存至: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存图表失败: {str(e)}")

    def save_plot_settings(self):
        """保存当前图表设置"""
        if not self.current_plot_params:
            QMessageBox.information(self, "提示", "请先绘制图表")
            return
        
        # 打开文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图表设置", "", "JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        # 确保文件扩展名为.json
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        try:
            # 准备要保存的设置
            settings = {
                "plot_type": self.current_plot_params.get("plot_type"),
                "x_col": self.current_plot_params.get("x_col"),
                "y_col": self.current_plot_params.get("y_col"),
                "color": self.current_plot_params.get("color"),
                "title": self.title_edit.text(),
                "x_label": self.x_label_edit.text(),
                "y_label": self.y_label_edit.text()
            }
            
            # 根据图表类型添加特定设置
            if settings["plot_type"] == "带误差棒的散点图":
                settings["xerr_col"] = self.current_plot_params.get("xerr_col")
                settings["yerr_col"] = self.current_plot_params.get("yerr_col")
            elif settings["plot_type"] in ["直方图", "2D密度图"]:
                settings["bins"] = self.current_plot_params.get("bins")
            
            # 保存设置到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            
            QMessageBox.information(self, "成功", f"图表设置已保存至: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存图表设置失败: {str(e)}")

    def load_plot_settings(self):
        """加载图表设置"""
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载图表设置", "", "JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # 从文件加载设置
            with open(file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 更新UI
            self.title_edit.setText(settings.get("title", ""))
            self.x_label_edit.setText(settings.get("x_label", ""))
            self.y_label_edit.setText(settings.get("y_label", ""))
            
            # 通知用户
            QMessageBox.information(self, "成功", "图表设置已加载，请重新绘制图表应用这些设置")
            
            # 返回加载的设置
            return settings
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载图表设置失败: {str(e)}")
            return None