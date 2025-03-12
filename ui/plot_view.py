from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QGroupBox, QFormLayout, QLineEdit,
                            QMessageBox, QFileDialog, QProgressDialog)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, pyqtSlot, QSize  # 添加QSize导入
import matplotlib
matplotlib.use('QtAgg')

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
        from core.visualization import PlotCanvas
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
    
    @pyqtSlot()  # 修改装饰器，移除dict参数
    def apply_settings(self):
        """应用新的图表设置"""
        if not self.current_plot_params:
            QMessageBox.information(self, "提示", "请先生成图表后再应用设置")
            return
        
        # 更新当前参数中的设置
        self.current_plot_params['title'] = self.title_edit.text() or None
        self.current_plot_params['x_label'] = self.x_label_edit.text() or None
        self.current_plot_params['y_label'] = self.y_label_edit.text() or None
        
        # 重新处理绘图请求
        self.handle_plot_request(self.current_plot_params.copy())

   
    @pyqtSlot()
    def save_plot_settings(self):
        """保存图表设置"""
        if not self.current_plot_params:
            QMessageBox.information(self, "提示", "请先生成图表后再保存设置")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "保存图表设置", 
            "", 
            "JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                # 提取需要保存的设置
                settings = {
                    'title': self.title_edit.text(),
                    'x_label': self.x_label_edit.text(),
                    'y_label': self.y_label_edit.text(),
                    'plot_type': self.current_plot_params.get('plot_type'),
                    'color': self.current_plot_params.get('color', 'blue'),
                    'mark_style': self.current_plot_params.get('mark_style', 'o'),
                    'mark_size': self.current_plot_params.get('mark_size', 10),
                    'bins': self.current_plot_params.get('bins', 10)
                }
                
                import json
                with open(file_path, 'w') as f:
                    json.dump(settings, f, indent=4)
                
                QMessageBox.information(self, "成功", "图表设置已保存")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
    
    @pyqtSlot()
    def load_plot_settings(self):
        """加载图表设置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "加载图表设置", 
            "", 
            "JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                
                # 应用加载的设置
                if 'title' in settings:
                    self.title_edit.setText(settings['title'])
                if 'x_label' in settings:
                    self.x_label_edit.setText(settings['x_label'])
                if 'y_label' in settings:
                    self.y_label_edit.setText(settings['y_label'])
                
                # 如果当前有绘图参数，更新它
                if self.current_plot_params:
                    self.current_plot_params.update({
                        'title': settings.get('title'),
                        'x_label': settings.get('x_label'),
                        'y_label': settings.get('y_label'),
                        'color': settings.get('color', self.current_plot_params.get('color', 'blue')),
                        'mark_style': settings.get('mark_style', self.current_plot_params.get('mark_style', 'o')),
                        'mark_size': settings.get('mark_size', self.current_plot_params.get('mark_size', 10)),
                        'bins': settings.get('bins', self.current_plot_params.get('bins', 10))
                    })
                    
                    # 重新绘制图表
                    self.handle_plot_request(self.current_plot_params.copy())
                
                QMessageBox.information(self, "成功", "图表设置已加载")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载设置失败: {str(e)}")
    
    @pyqtSlot()
    def save_plot(self):
        """保存当前图表为图片"""
        if not hasattr(self, 'canvas') or not self.canvas:
            QMessageBox.warning(self, "警告", "没有可保存的图表")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "保存图表", 
            "", 
            "PNG图片 (*.png);;JPEG图片 (*.jpg);;PDF文档 (*.pdf);;SVG图片 (*.svg);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                # 显示进度对话框
                progress = QProgressDialog("正在保存图表...", "取消", 0, 100, self)
                progress.setWindowTitle("保存中")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.show()
                progress.setValue(10)
                
                # 保存图表
                self.canvas.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                
                progress.setValue(100)
                QMessageBox.information(self, "成功", "图表已保存")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存图表失败: {str(e)}")

    @pyqtSlot(dict)
    def handle_plot_request(self, plot_params):
        """处理绘图请求"""
        if not plot_params or 'data' not in plot_params:
            QMessageBox.warning(self, "错误", "无效的绘图参数")
            return
        
        # 获取当前图表设置
        title = self.title_edit.text()
        x_label = self.x_label_edit.text()
        y_label = self.y_label_edit.text()
        
        # 添加图表设置到绘图参数
        plot_params['title'] = title if title else None
        plot_params['x_label'] = x_label if x_label else None
        plot_params['y_label'] = y_label if y_label else None
        
        # 存储当前绘图参数以便应用设置时使用
        self.current_plot_params = plot_params.copy()
        
        # 根据绘图类型调用相应的绘图方法
        plot_type = plot_params.get('plot_type')
        data = plot_params['data']
        x_col = plot_params['x_col']
        color = plot_params.get('color', 'blue')
        
        success = False
        message = ""
        
        try:
            if plot_type == "散点图":
                success, message = self.visualizer.scatter_plot(
                    data=plot_params['data'],
                    x_col=plot_params['x_col'],
                    y_col=plot_params['y_col'],
                    title=plot_params['title'],
                    x_label=plot_params['x_label'],
                    y_label=plot_params['y_label'],
                    color=plot_params.get('color', 'blue'),
                    mark_style=plot_params.get('mark_style', 'o'),
                    mark_size=plot_params.get('mark_size', 10)
                )
            elif plot_type == "带误差棒的散点图":
                success, message = self.visualizer.scatter_plot_with_error(
                    data=plot_params['data'],
                    x_col=plot_params['x_col'],
                    y_col=plot_params['y_col'],
                    xerr_col=plot_params.get('xerr_col'),
                    yerr_col=plot_params.get('yerr_col'),
                    title=plot_params['title'],
                    x_label=plot_params['x_label'],
                    y_label=plot_params['y_label'],
                    color=plot_params.get('color', 'blue'),
                    mark_style=plot_params.get('mark_style', 'o'),
                    mark_size=plot_params.get('mark_size', 10)
                )
            elif plot_type == "直方图":
                bins = plot_params.get("bins", 10)
                success, message = self.visualizer.histogram(
                    data=data, 
                    col=x_col, 
                    bins=bins, 
                    title=plot_params['title'],
                    x_label=plot_params['x_label'],
                    y_label=plot_params['y_label'],
                    color=color
                )
                
            elif plot_type == "2D密度图":
                y_col = plot_params["y_col"]
                bins = plot_params.get("bins", 20)
                success, message = self.visualizer.density_map_2d(
                    data=data, 
                    x_col=x_col, 
                    y_col=y_col, 
                    bins=bins,
                    title=plot_params['title'],
                    x_label=plot_params['x_label'],
                    y_label=plot_params['y_label']
                )
            
            else:
                success = False
                message = f"未知的绘图类型: {plot_type}"
        except Exception as e:
            success = False
            message = f"绘图错误: {str(e)}"
            
        # 显示结果消息
        if not success:
            QMessageBox.warning(self, "绘图错误", message)