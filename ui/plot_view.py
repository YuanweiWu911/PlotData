import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QGroupBox, QFormLayout, QLineEdit, QApplication,
                            QMessageBox, QFileDialog, QProgressDialog, 
                            QDoubleSpinBox, QLabel, QSpinBox, QCheckBox,
                            QComboBox, QColorDialog)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
import matplotlib
from PyQt6.QtGui import QDoubleValidator, QColor
matplotlib.use('QtAgg')

class PlotView(QWidget):
    """绘图视图组件"""
    
    # 添加信号，用于通知其他组件切换设置区域的显示状态
    settings_visibility_changed = pyqtSignal(bool)
    
    # 添加从data_view.py移动过来的信号
    plot_requested = pyqtSignal(str, str, str, str, str, str, str, int, str, int, str)
    
    def __init__(self, data_manager, visualizer):
        super().__init__()
        
        self.data_manager = data_manager
        self.visualizer = visualizer
        
        # 初始化UI
        self.init_ui()
        
        # 添加数据管理器的信号连接
        if hasattr(self.data_manager, 'data_changed'):
            self.data_manager.data_changed.connect(self.update_columns)
        
        # 初始化时尝试更新列
        self.update_columns()
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建工具栏
        toolbar_layout = QHBoxLayout()
        
        # 添加绘图设置切换按钮到工具栏
        self.toggle_settings_button = QPushButton("绘图设置")
        self.toggle_settings_button.setCheckable(True)  # 设置为可切换状态
        self.toggle_settings_button.setChecked(True)    # 默认为显示状态
        self.toggle_settings_button.clicked.connect(self.toggle_settings_visibility)
        self.toggle_settings_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView))
        toolbar_layout.addWidget(self.toggle_settings_button)
        
        # 添加保存设置按钮到工具栏
        self.save_settings_toolbar_button = QPushButton("保存设置")
        self.save_settings_toolbar_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton))
        self.save_settings_toolbar_button.clicked.connect(self.save_plot_settings)
        toolbar_layout.addWidget(self.save_settings_toolbar_button)
        
        # 添加加载设置按钮到工具栏
        self.load_settings_toolbar_button = QPushButton("加载设置")
        self.load_settings_toolbar_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogOpenButton))
        self.load_settings_toolbar_button.clicked.connect(self.load_plot_settings)
        toolbar_layout.addWidget(self.load_settings_toolbar_button)
        
        # 添加保存图表按钮到工具栏
        self.save_plot_toolbar_button = QPushButton("保存图表")
        self.save_plot_toolbar_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton))
        self.save_plot_toolbar_button.clicked.connect(self.save_plot)
        toolbar_layout.addWidget(self.save_plot_toolbar_button)
        
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)
        
        # 创建绘图区域
        plot_group = QGroupBox("绘图区域")
        plot_layout = QVBoxLayout(plot_group)
        
        # 创建画布
        from core.visualization import PlotCanvas
        if hasattr(self, 'canvas'):
            self.canvas.deleteLater()
        self.canvas = PlotCanvas(self, width=5, height=4)
        plot_layout.addWidget(self.canvas)
        
        # 设置可视化器的画布
        self.visualizer.set_canvas(self.canvas)
        
        main_layout.addWidget(plot_group)
        
        # 创建图表设置区域
        settings_group = QGroupBox("绘图设置")
        settings_layout = QFormLayout(settings_group)
        
        # 从data_view.py移动过来的绘图控制区域
        # 创建绘图控制区域
        plot_control_layout = QVBoxLayout()

        # 样式设置
        style_layout = QHBoxLayout()

         # 绘图类型选择
#       plot_type_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("绘图类型:"))
        
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["散点图", "带误差棒的散点图", "直方图", "2D密度图"])
        self.plot_type_combo.currentIndexChanged.connect(self.on_plot_type_changed)
        style_layout.addWidget(self.plot_type_combo)
        
        # 颜色选择
        style_layout.addWidget(QLabel(""))
        self.color_button = QPushButton("颜色选择")
        self.color_button.setFixedWidth(60)
        self.color_button.setStyleSheet("background-color: blue;")
        self.color_button.setProperty("color", "blue")  # 存储颜色值
        self.color_button.clicked.connect(self.choose_color)
        style_layout.addWidget(self.color_button)
        
        # 标记样式
        style_layout.addWidget(QLabel("Marker样式"))
        self.mark_style_combo = QComboBox()
        self.mark_style_combo.addItems(["o", "s", "^", "v", "D", "*", "+", "x"])
        style_layout.addWidget(self.mark_style_combo)
        
        # 标记大小
        style_layout.addWidget(QLabel("Marker大小"))
        self.mark_size_spin = QSpinBox()
        self.mark_size_spin.setRange(1, 30)
        self.mark_size_spin.setValue(10)
        style_layout.addWidget(self.mark_size_spin)
        
        plot_control_layout.addLayout(style_layout)
       
        # 数据列选择
        columns_container = QWidget()  # 创建一个容器来包含列选择布局
        columns_layout = QHBoxLayout(columns_container)
        columns_layout.setContentsMargins(0, 0, 0, 0)  # 移除内边距
        
        # X轴列选择
        columns_layout.addWidget(QLabel("X轴数据:"))
        self.x_combo = QComboBox()
        columns_layout.addWidget(self.x_combo)
        
        # Y轴列选择
        columns_layout.addWidget(QLabel("Y轴数据:"))
        self.y_combo = QComboBox()
        columns_layout.addWidget(self.y_combo)
        
        plot_control_layout.addWidget(columns_container)  # 添加容器而不是布局

        # 误差棒列选择 - 将其放入单独的容器中
        self.error_settings = QWidget()
        error_layout = QHBoxLayout(self.error_settings)
        error_layout.setContentsMargins(0, 0, 0, 0)  # 移除内边距，确保与columns_container一致
        
        error_layout.addWidget(QLabel("X轴误差:"))
        self.xerr_combo = QComboBox()
        error_layout.addWidget(self.xerr_combo)
        
        error_layout.addWidget(QLabel("Y轴误差:"))
        self.yerr_combo = QComboBox()
        error_layout.addWidget(self.yerr_combo)
        
        plot_control_layout.addWidget(self.error_settings)
        
        # 直方图特有设置
        self.hist_settings = QWidget()
        hist_layout = QHBoxLayout(self.hist_settings)
        
        hist_layout.addWidget(QLabel("直方图类型:"))
        self.histtype_combo = QComboBox()
        self.histtype_combo.addItems(["bar", "barstacked", "step", "stepfilled"])
        hist_layout.addWidget(self.histtype_combo)
        
        hist_layout.addWidget(QLabel("分箱数:"))
        self.bins_spin = QSpinBox()
        self.bins_spin.setRange(5, 200)
        self.bins_spin.setValue(50)
        hist_layout.addWidget(self.bins_spin)
        
        self.hist_settings.setVisible(False)  # 默认隐藏
        plot_control_layout.addWidget(self.hist_settings)
        
        # 2D密度图特有设置
        self.density_settings = QWidget()
        density_layout = QHBoxLayout(self.density_settings)
        
        density_layout.addWidget(QLabel("颜色映射:"))
        self.colorbar_combo = QComboBox()
        self.colorbar_combo.addItems(["viridis", "plasma", "inferno", "magma", "cividis", 
                                     "Greys", "Purples", "Blues", "Greens", "Oranges", "Reds",
                                     "YlOrBr", "YlOrRd", "OrRd", "PuRd", "RdPu", "BuPu",
                                     "GnBu", "PuBu", "YlGnBu", "PuBuGn", "BuGn", "YlGn",
                                     "jet", "turbo", "rainbow", "coolwarm", "bwr", "seismic"])
        density_layout.addWidget(self.colorbar_combo)
        
        density_layout.addWidget(QLabel("分辨率:"))
        self.density_bins_spin = QSpinBox()
        self.density_bins_spin.setRange(10, 500)
        self.density_bins_spin.setValue(100)
        density_layout.addWidget(self.density_bins_spin)
        
        self.density_settings.setVisible(False)  # 默认隐藏
        plot_control_layout.addWidget(self.density_settings)
        
        # 绘图按钮
        self.plot_button = QPushButton("生成图表")
        self.plot_button.setMinimumHeight(30)  # 设置更大的高度
        self.plot_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* 绿色 */
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;  /* 鼠标悬停时的深绿色 */
            }
        """)
        self.plot_button.clicked.connect(self.request_plot)
        plot_control_layout.addWidget(self.plot_button)
        
        # 将绘图控制添加到设置布局
        settings_layout.addRow("", plot_control_layout)
        
        # 标题设置
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("标题:")
        settings_layout.addRow("", self.title_edit)
        
        # 添加X轴刻度设置
        x_ticks_layout = QHBoxLayout()
        
        # X轴标签设置
        self.x_label_edit = QLineEdit()
        self.x_label_edit.setPlaceholderText("X轴标签:")

        self.x_ticks_min = QLineEdit()
        self.x_ticks_min.setPlaceholderText("X轴最小值（支持科学计数法）")

        self.x_ticks_min.setValidator(QDoubleValidator(notation=QDoubleValidator.Notation.ScientificNotation))
        x_ticks_layout.addWidget(self.x_label_edit)
        x_ticks_layout.addWidget(QLabel("X轴范围:"))
        x_ticks_layout.addWidget(self.x_ticks_min)

        self.x_ticks_max = QLineEdit()
        self.x_ticks_max.setPlaceholderText("X轴最大值")
        self.x_ticks_max.setValidator(QDoubleValidator(notation=QDoubleValidator.Notation.ScientificNotation))
        x_ticks_layout.addWidget(QLabel("-"))
        x_ticks_layout.addWidget(self.x_ticks_max)
        
        settings_layout.addRow("", x_ticks_layout)
        
        # 添加Y轴刻度设置
        y_ticks_layout = QHBoxLayout()
        
        # Y轴标签设置
        self.y_label_edit = QLineEdit()
        self.y_label_edit.setPlaceholderText("Y轴标签:")

        self.y_ticks_min = QLineEdit()
        self.y_ticks_min.setPlaceholderText("Y轴最小值")
        self.y_ticks_min.setValidator(QDoubleValidator(notation=QDoubleValidator.Notation.ScientificNotation))
        y_ticks_layout.addWidget(self.y_label_edit)
        y_ticks_layout.addWidget(QLabel("Y轴范围:"))
        y_ticks_layout.addWidget(self.y_ticks_min)
        
        self.y_ticks_max = QLineEdit()
        self.y_ticks_max.setPlaceholderText("Y轴最大值")
        self.y_ticks_max.setValidator(QDoubleValidator(notation=QDoubleValidator.Notation.ScientificNotation))
        y_ticks_layout.addWidget(QLabel("-"))
        y_ticks_layout.addWidget(self.y_ticks_max)

        settings_layout.addRow("", y_ticks_layout)

        # 添加刻度数量设置
        ticks_layout = QHBoxLayout()

        # X轴刻度设置
        x_ticks_group = QGroupBox("X轴刻度设置")
        x_ticks_layout = QHBoxLayout()
        
        self.x_major_ticks_spin = QSpinBox()
        self.x_major_ticks_spin.setRange(0, 50)
        self.x_major_ticks_spin.setValue(5)
        x_ticks_layout.addWidget(QLabel("主刻度数:"))
        x_ticks_layout.addWidget(self.x_major_ticks_spin)
        
        self.x_minor_ticks_spin = QSpinBox()
        self.x_minor_ticks_spin.setRange(0, 10)
        self.x_minor_ticks_spin.setValue(1)
        x_ticks_layout.addWidget(QLabel("次刻度数:"))
        x_ticks_layout.addWidget(self.x_minor_ticks_spin)
        
        self.x_grid_checkbox = QCheckBox("显示网格线")
        self.x_grid_checkbox.setChecked(True)
        x_ticks_layout.addWidget(self.x_grid_checkbox)
        
        x_ticks_group.setLayout(x_ticks_layout)
        ticks_layout.addWidget(x_ticks_group)
        
        # Y轴刻度设置
        y_ticks_group = QGroupBox("Y轴刻度设置")
        y_ticks_layout = QHBoxLayout()
        
        self.y_major_ticks_spin = QSpinBox()
        self.y_major_ticks_spin.setRange(0, 50)
        self.y_major_ticks_spin.setValue(5)
        y_ticks_layout.addWidget(QLabel("主刻度数:"))
        y_ticks_layout.addWidget(self.y_major_ticks_spin)
        
        self.y_minor_ticks_spin = QSpinBox()
        self.y_minor_ticks_spin.setRange(0, 10)
        self.y_minor_ticks_spin.setValue(1)
        y_ticks_layout.addWidget(QLabel("次刻度数:"))
        y_ticks_layout.addWidget(self.y_minor_ticks_spin)
        
        self.y_grid_checkbox = QCheckBox("显示网格线")
        self.y_grid_checkbox.setChecked(True)
        y_ticks_layout.addWidget(self.y_grid_checkbox)
        
        y_ticks_group.setLayout(y_ticks_layout)
        ticks_layout.addWidget(y_ticks_group)
        
        settings_layout.addRow("", ticks_layout)

        # 删除原有的设置刻度按钮相关代码
        main_layout.addWidget(settings_group)

        # 存储当前绘图参数
        self.current_plot_params = None


    @pyqtSlot()  # 修改装饰器，移除dict参数
    def apply_settings(self):
        """应用新的图表设置"""
        if not self.current_plot_params:
            QMessageBox.information(self, "提示", "请先生成图表后再应用设置")
            return
        
        try:
            x_min = float(self.x_ticks_min.text()) if self.x_ticks_min.text() else None
            x_max = float(self.x_ticks_max.text()) if self.x_ticks_max.text() else None
            y_min = float(self.y_ticks_min.text()) if self.y_ticks_min.text() else None
            y_max = float(self.y_ticks_max.text()) if self.y_ticks_max.text() else None
        except ValueError:
            x_min, x_max, y_min, y_max = None, None, None, None
            print("坐标轴范围设置格式无效，将使用自动范围")
        
        # 更新当前参数中的设置
        self.current_plot_params['title'] = self.title_edit.text() or None
        self.current_plot_params['x_label'] = self.x_label_edit.text() or None
        self.current_plot_params['y_label'] = self.y_label_edit.text() or None
        self.current_plot_params['x_min'] = x_min
        self.current_plot_params['x_max'] = x_max
        self.current_plot_params['y_min'] = y_min
        self.current_plot_params['y_max'] = y_max
        
        # 添加刻度和网格线设置
        self.current_plot_params['x_major_ticks'] = self.x_major_ticks_spin.value()
        self.current_plot_params['x_minor_ticks'] = self.x_minor_ticks_spin.value()
        self.current_plot_params['x_show_grid'] = self.x_grid_checkbox.isChecked()
        self.current_plot_params['y_major_ticks'] = self.y_major_ticks_spin.value()
        self.current_plot_params['y_minor_ticks'] = self.y_minor_ticks_spin.value()
        self.current_plot_params['y_show_grid'] = self.y_grid_checkbox.isChecked()
        
        # 重新处理绘图请求 - 添加histtype和bins参数
        self.handle_plot_request(
            self.current_plot_params.get('plot_type', ''),
            self.current_plot_params.get('x_col', ''),
            self.current_plot_params.get('y_col', ''),
            self.current_plot_params.get('color', 'blue'),
            self.current_plot_params.get('xerr_col', None),
            self.current_plot_params.get('yerr_col', None),
            self.current_plot_params.get('mark_style', 'o'),
            self.current_plot_params.get('mark_size', 10),
            self.current_plot_params.get('histtype', 'bar'),  # 添加histtype参数
            self.current_plot_params.get('bins', 10),         # 添加bins参数
            self.current_plot_params.get('colormap', 'viridis')  # 添加colormap参数
        )
   
    @pyqtSlot()
    def save_plot_settings(self):
        """保存图表设置"""
        if not self.current_plot_params:
            QMessageBox.information(self, "提示", "请先生成图表后再保存设置")
            return
            
        # 获取主窗口中的data_view实例
        main_window = self.window()
        data_view = main_window.data_view if hasattr(main_window, 'data_view') else None
    
        # 获取当前数据文件路径
        current_file_path = ""
        if hasattr(self.data_manager, 'current_file') and self.data_manager.current_file:
            current_file_path = self.data_manager.current_file
        elif 'data_file_path' in self.current_plot_params:
            current_file_path = self.current_plot_params.get('data_file_path', '')
        
        # 处理坐标轴范围设置
        try:
            x_min = float(self.x_ticks_min.text()) if self.x_ticks_min.text() else None
            x_max = float(self.x_ticks_max.text()) if self.x_ticks_max.text() else None
            y_min = float(self.y_ticks_min.text()) if self.y_ticks_min.text() else None
            y_max = float(self.y_ticks_max.text()) if self.y_ticks_max.text() else None
        except ValueError:
            x_min, x_max, y_min, y_max = None, None, None, None
            print("坐标轴范围设置格式无效，将使用None值")
        
        # 提取需要保存的设置 - 修改为使用当前类(self)的控件而不是data_view的控件
        settings = {
            # 数据文件信息
            'data_file_path': current_file_path,
            
            # 数据筛选参数
            'filter_expr': data_view.filter_expr_edit.toPlainText() if data_view else '',
            
            # 绘图控制参数 - 修改为使用self的控件
            'x_col': self.x_combo.currentText(),
            'y_col': self.y_combo.currentText(),
            'xerr_col': self.xerr_combo.currentText(),
            'yerr_col': self.yerr_combo.currentText(),
            
            # 图表样式参数 - 修改为使用self的控件
            'plot_type': self.plot_type_combo.currentText(),
            'color': self.color_button.property("color") if self.color_button.property("color") else 'blue',
            'mark_style': self.mark_style_combo.currentText(),
            'mark_size': self.mark_size_spin.value(),
    
            # 直方图特有参数 - 修改为使用self的控件
            'histtype': self.histtype_combo.currentText() if hasattr(self, 'histtype_combo') else 'bar',
            'bins': self.bins_spin.value() if hasattr(self, 'bins_spin') else 50,
    
            # 2D densitymap 参数 - 修改为使用self的控件
            'colormap': self.colorbar_combo.currentText() if hasattr(self, 'colorbar_combo') else 'viridis',
            
            # 图表显示设置
            'title': self.title_edit.text(),
            'x_label': self.x_label_edit.text(),
            'y_label': self.y_label_edit.text(),
            
            # 新增坐标轴刻度和网格线设置
            'x_major_ticks': self.x_major_ticks_spin.value(),
            'x_minor_ticks': self.x_minor_ticks_spin.value(),
            'x_show_grid': self.x_grid_checkbox.isChecked(),
            'y_major_ticks': self.y_major_ticks_spin.value(),
            'y_minor_ticks': self.y_minor_ticks_spin.value(),
            'y_show_grid': self.y_grid_checkbox.isChecked(),
            
            # 新增坐标轴范围设置
            'x_min': x_min,
            'x_max': x_max,
            'y_min': y_min,
            'y_max': y_max
        }
        
        # 打印调试信息
        print(f"保存设置 - 数据文件路径: {settings['data_file_path']}")
        
        # 设置默认保存路径为当前数据文件所在目录
        default_dir = ""
        if settings['data_file_path']:
            default_dir = os.path.dirname(settings['data_file_path'])
            # 提取文件名作为默认保存名
            base_name = os.path.splitext(os.path.basename(settings['data_file_path']))[0]
            default_path = os.path.join(default_dir, f"{base_name}_plot.json")
        else:
            default_path = ""
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "保存图表设置", 
            default_path, 
            "JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=4, ensure_ascii=False)
                
                QMessageBox.information(self, "成功", f"图表设置已保存到\n{file_path}")
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
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 获取主窗口中的data_view实例
                main_window = self.window()
                data_view = main_window.data_view if hasattr(main_window, 'data_view') else None

                # 1. 首先加载数据文件 - 优先处理
                data_file_path = settings.get('data_file_path')
                if data_file_path:
                    if os.path.exists(data_file_path):
                        # 显示加载进度对话框
                        progress = QProgressDialog("正在加载数据文件...", "取消", 0, 100, self)
                        progress.setWindowTitle("加载中")
                        progress.setWindowModality(Qt.WindowModality.WindowModal)
                        progress.show()
                        progress.setValue(10)
                        
                        # 加载文件
                        main_window.open_file(data_file_path)
                        progress.setValue(50)
                        QApplication.processEvents()  # 等待数据加载完成
                        progress.setValue(100)
                    else:
                        QMessageBox.warning(
                            self, 
                            "文件不存在", 
                            f"无法找到原始数据文件:\n{data_file_path}\n\n将继续加载其他设置。"
                        )

                # 2. 应用筛选条件
                if data_view and self.data_manager.get_data() is not None:
                    filter_expr = settings.get('filter_expr')
                    if filter_expr:
                        data_view.filter_expr_edit.setPlainText(filter_expr)
                        data_view.apply_filter()
                        QApplication.processEvents()

                # 3. 设置绘图参数 - 修改为使用self的控件
                # 设置颜色并保存属性
                color = settings.get('color', 'blue')
                self.color_button.setStyleSheet(f"background-color: {color};")
                self.color_button.setProperty("color", color)
                
                # 设置其他参数
                self.plot_type_combo.setCurrentText(settings.get('plot_type', '散点图'))
                self.mark_style_combo.setCurrentText(settings.get('mark_style', 'o'))
                self.mark_size_spin.setValue(settings.get('mark_size', 10))

                # 设置直方图特有参数
                histtype = settings.get('histtype', 'bar')
                index = self.histtype_combo.findText(histtype)
                if index >= 0:
                    self.histtype_combo.setCurrentIndex(index)
            
                # 设置分箱数量（适用于直方图和2D密度图）
                self.bins_spin.setValue(settings.get('bins', 50))
                
                # 设置Colorbar样式（2D密度图）
                colormap = settings.get('colormap')
                if colormap:
                    index = self.colorbar_combo.findText(colormap)
                    if index >= 0:
                        self.colorbar_combo.setCurrentIndex(index)
            
                # 触发绘图类型变更事件以更新界面
                self.on_plot_type_changed(self.plot_type_combo.currentIndex())

                # 设置数据列
                self.x_combo.setCurrentText(settings.get('x_col', ''))
                self.y_combo.setCurrentText(settings.get('y_col', ''))
                self.xerr_combo.setCurrentText(settings.get('xerr_col', ''))
                self.yerr_combo.setCurrentText(settings.get('yerr_col', ''))

                # 4. 更新图表显示设置
                self.title_edit.setText(settings.get('title', ''))
                self.x_label_edit.setText(settings.get('x_label', ''))
                self.y_label_edit.setText(settings.get('y_label', ''))
                
                # 新增：加载坐标轴刻度和网格线设置
                self.x_major_ticks_spin.setValue(settings.get('x_major_ticks', 5))
                self.x_minor_ticks_spin.setValue(settings.get('x_minor_ticks', 1))
                self.x_grid_checkbox.setChecked(settings.get('x_show_grid', True))
                self.y_major_ticks_spin.setValue(settings.get('y_major_ticks', 5))
                self.y_minor_ticks_spin.setValue(settings.get('y_minor_ticks', 1))
                self.y_grid_checkbox.setChecked(settings.get('y_show_grid', True))
                
                # 新增：加载坐标轴范围设置
                if 'x_min' in settings and settings['x_min'] is not None:
                    self.x_ticks_min.setText(str(settings['x_min']))
                else:
                    self.x_ticks_min.clear()
                    
                if 'x_max' in settings and settings['x_max'] is not None:
                    self.x_ticks_max.setText(str(settings['x_max']))
                else:
                    self.x_ticks_max.clear()
                    
                if 'y_min' in settings and settings['y_min'] is not None:
                    self.y_ticks_min.setText(str(settings['y_min']))
                else:
                    self.y_ticks_min.clear()
                    
                if 'y_max' in settings and settings['y_max'] is not None:
                    self.y_ticks_max.setText(str(settings['y_max']))
                else:
                    self.y_ticks_max.clear()
                
                # 5. 触发绘图
                if data_view and self.data_manager.get_data() is not None:
                    data_view.request_plot()
                    QMessageBox.information(self, "成功", "设置已完整加载并应用")
                else:
                    QMessageBox.information(self, "部分成功", "图表设置已加载，但未能加载数据或生成图表")
                
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

    @pyqtSlot(str, str, str, str, str, str, str, int, str, int)
    def handle_plot_request(self, plot_type, x_col, y_col, color,
        xerr_col, yerr_col, mark_style, mark_size,
        histtype='bar', bins=10, colormap = None):
        """处理绘图请求"""
        try:
            # 获取新增设置参数
            x_major_ticks = self.x_major_ticks_spin.value()
            x_minor_ticks = self.x_minor_ticks_spin.value()
            x_show_grid = self.x_grid_checkbox.isChecked()
            
            y_major_ticks = self.y_major_ticks_spin.value()
            y_minor_ticks = self.y_minor_ticks_spin.value()
            y_show_grid = self.y_grid_checkbox.isChecked()

            # 获取坐标轴范围设置并转换为浮点数
            try:
                x_min = float(self.x_ticks_min.text()) if self.x_ticks_min.text() else None
                x_max = float(self.x_ticks_max.text()) if self.x_ticks_max.text() else None
                y_min = float(self.y_ticks_min.text()) if self.y_ticks_min.text() else None
                y_max = float(self.y_ticks_max.text()) if self.y_ticks_max.text() else None
            except ValueError:
                x_min, x_max, y_min, y_max = None, None, None, None
                print("坐标轴范围设置格式无效，将使用自动范围")

            # 获取数据
            data = self.data_manager.get_data(filtered=True)
            if data is None or data.empty:
                QMessageBox.warning(self, "错误", "没有可用的数据进行绘图")
                return
                
            # 获取图表设置
            title = self.title_edit.text()
            x_label = self.x_label_edit.text()
            y_label = self.y_label_edit.text()
            
            # 构建当前绘图参数以便后续应用设置
            self.current_plot_params = {
                'plot_type': plot_type,
                'x_col': x_col,
                'y_col': y_col,
                'color': color,
                'xerr_col': xerr_col,
                'yerr_col': yerr_col,
                'mark_style': mark_style,
                'mark_size': mark_size,
                'histtype': histtype,
                'bins': bins,
                'title': title,
                'x_label': x_label,
                'y_label': y_label,
                'colormap': colormap,
                # 修正刻度设置参数名称，使用与save_plot_settings一致的键名
                'x_min': x_min,
                'x_max': x_max,
                'y_min': y_min,
                'y_max': y_max,
                'x_major_ticks': x_major_ticks,
                'x_minor_ticks': x_minor_ticks,
                'x_show_grid': x_show_grid,
                'y_major_ticks': y_major_ticks,
                'y_minor_ticks': y_minor_ticks,
                'y_show_grid': y_show_grid
            }
            
            # 根据图表类型调用不同的绘图方法
            if plot_type == "散点图":
                # 散点图代码，添加坐标轴范围参数 - 修正参数名称
                success, message = self.visualizer.scatter_plot(
                    data=data,
                    x_col=x_col,
                    y_col=y_col,
                    title=title,
                    x_label=x_label,
                    y_label=y_label,
                    color=color,
                    mark_size=mark_size,
                    mark_style=mark_style,
                    x_major_ticks=x_major_ticks,  # 修改为X轴主刻度
                    x_minor_ticks=x_minor_ticks,  # 修改为X轴次刻度
                    x_show_grid=x_show_grid,      # 修改为X轴网格线
                    y_major_ticks=y_major_ticks,  # 添加Y轴主刻度
                    y_minor_ticks=y_minor_ticks,  # 添加Y轴次刻度
                    y_show_grid=y_show_grid,      # 添加Y轴网格线
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max
                )
            elif plot_type == "带误差棒的散点图":
                # 误差棒散点图代码，添加坐标轴范围参数 - 修正参数名称
                success, message = self.visualizer.scatter_plot_with_error(
                    data=data,
                    x_col=x_col,
                    y_col=y_col,
                    xerr_col=xerr_col,
                    yerr_col=yerr_col,
                    title=title,
                    x_label=x_label,
                    y_label=y_label,
                    color=color,
                    mark_size=mark_size,
                    mark_style=mark_style,
                    x_major_ticks=x_major_ticks,
                    x_minor_ticks=x_minor_ticks,
                    x_show_grid=x_show_grid,
                    y_major_ticks=y_major_ticks,
                    y_minor_ticks=y_minor_ticks,
                    y_show_grid=y_show_grid,
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max
                )
            elif plot_type == "直方图":
                # 直方图使用专门的参数，添加坐标轴范围参数 - 修正参数名称
                valid_histtypes = ['bar', 'barstacked', 'step', 'stepfilled']
                # 验证histtype参数
                valid_histtype = histtype if histtype in valid_histtypes else 'bar'
                
                success, message = self.visualizer.histogram(
                    data=data,
                    col=x_col,
                    bins=bins,
                    title=title,
                    x_label=x_label,
                    y_label=y_label,
                    color=color,
                    histtype=valid_histtype,
                    edgecolor='black',
                    hatch='/',
                    x_major_ticks=x_major_ticks,
                    x_minor_ticks=x_minor_ticks,
                    x_show_grid=x_show_grid,
                    y_major_ticks=y_major_ticks,
                    y_minor_ticks=y_minor_ticks,
                    y_show_grid=y_show_grid,
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max
                )
            elif plot_type == "2D密度图":
                # 2D密度图代码，添加坐标轴范围参数 - 修正参数名称
                success, message = self.visualizer.density_map_2d(
                    data=data,
                    x_col=x_col,
                    y_col=y_col,
                    bins=bins,
                    title=title,
                    x_label=x_label,
                    y_label=y_label,
                    colormap=colormap,
                    x_major_ticks=x_major_ticks,
                    x_minor_ticks=x_minor_ticks,
                    x_show_grid=x_show_grid,
                    y_major_ticks=y_major_ticks,
                    y_minor_ticks=y_minor_ticks,
                    y_show_grid=y_show_grid,
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max
                )
            else:
                QMessageBox.warning(self, "错误", f"不支持的图表类型: {plot_type}")
                return
                
            # 显示绘图结果
            if not success:
                QMessageBox.warning(self, "绘图错误", message)
        
        except Exception as e:
            QMessageBox.critical(self, "绘图错误", f"绘图过程中发生错误: {str(e)}")

    @pyqtSlot()
    def update_columns(self):
        """更新列选择下拉框"""
        # 保存当前选择的值
        current_x = self.x_combo.currentText()
        current_y = self.y_combo.currentText()
        current_xerr = self.xerr_combo.currentText()
        current_yerr = self.yerr_combo.currentText()
        
        # 清空下拉框
        self.x_combo.clear()
        self.y_combo.clear()
        self.xerr_combo.clear()
        self.yerr_combo.clear()
        
        # 添加"无"选项到误差棒下拉框
        self.xerr_combo.addItem("无")
        self.yerr_combo.addItem("无")
        
        # 获取数据列
        columns = self.data_manager.get_column_names()
        if not columns:
            return
            
        # 添加列到下拉框
        self.x_combo.addItems(columns)
        self.y_combo.addItems(columns)
        self.xerr_combo.addItems(columns)
        self.yerr_combo.addItems(columns)
        
        # 尝试恢复之前的选择
        if current_x and current_x in columns:
            self.x_combo.setCurrentText(current_x)
        elif columns:
            self.x_combo.setCurrentIndex(0)  # 默认选择第一列
            
        if current_y and current_y in columns:
            self.y_combo.setCurrentText(current_y)
        elif len(columns) > 1:
            self.y_combo.setCurrentIndex(1)  # 默认选择第二列
        elif columns:
            self.y_combo.setCurrentIndex(0)  # 如果只有一列，选择第一列
            
        if current_xerr and current_xerr in columns:
            self.xerr_combo.setCurrentText(current_xerr)
        else:
            self.xerr_combo.setCurrentText("无")  # 默认不选择误差棒
            
        if current_yerr and current_yerr in columns:
            self.yerr_combo.setCurrentText(current_yerr)
        else:
            self.yerr_combo.setCurrentText("无")  # 默认不选择误差棒

    def on_plot_type_changed(self, index):
        """处理绘图类型变更"""
        plot_type = self.plot_type_combo.currentText()
        
        # 隐藏所有特殊设置
        self.error_settings.setVisible(False)
        self.hist_settings.setVisible(False)
        self.density_settings.setVisible(False)
        
        # 根据绘图类型显示相应设置
        if plot_type == "直方图":
            self.hist_settings.setVisible(True)
        elif plot_type == "2D密度图":
            self.density_settings.setVisible(True)
        elif plot_type == "带误差棒的散点图":
            self.error_settings.setVisible(True)
    
    def choose_color(self):
        """打开颜色选择对话框"""
        current_color = self.color_button.property("color")
        if current_color:
            initial_color = QColor(current_color)
        else:
            initial_color = QColor("blue")
            
        color = QColorDialog.getColor(initial_color, self, "选择颜色")
        if color.isValid():
            # 设置按钮背景色
            self.color_button.setStyleSheet(f"background-color: {color.name()};")
            # 存储颜色值
            self.color_button.setProperty("color", color.name())
    
    def request_plot(self):
        """请求绘图"""
        # 获取当前选择的列
        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()
        
        # 获取误差棒列
        xerr_col = self.xerr_combo.currentText()
        if xerr_col == "无":
            xerr_col = None
            
        yerr_col = self.yerr_combo.currentText()
        if yerr_col == "无":
            yerr_col = None
        
        # 获取绘图类型和样式
        plot_type = self.plot_type_combo.currentText()
        color = self.color_button.property("color") or "blue"
        mark_style = self.mark_style_combo.currentText()
        mark_size = self.mark_size_spin.value()
        
        # 获取特殊图表参数
        histtype = self.histtype_combo.currentText() if plot_type == "直方图" else "bar"
        bins = self.bins_spin.value() if plot_type == "直方图" else 50
        colormap = self.colorbar_combo.currentText() if plot_type == "2D密度图" else "viridis"
        
        # 检查必要的列是否已选择
        if not x_col:
            QMessageBox.warning(self, "错误", "请选择X轴列")
            return
            
        if plot_type != "直方图" and not y_col:
            QMessageBox.warning(self, "错误", "请选择Y轴列")
            return
            
        # 处理绘图请求
        self.handle_plot_request(
            plot_type=plot_type,
            x_col=x_col,
            y_col=y_col,
            color=color,
            xerr_col=xerr_col,
            yerr_col=yerr_col,
            mark_style=mark_style,
            mark_size=mark_size,
            histtype=histtype,
            bins=bins,
            colormap=colormap
        )
    
    def toggle_settings_visibility(self):
        """切换设置区域的显示状态"""
        # 这个方法在原始代码中已经存在，但需要添加信号发射
        is_visible = self.toggle_settings_button.isChecked()
        
        # 设置设置区域的可见性
        if hasattr(self, 'settings_group'):
            self.settings_group.setVisible(is_visible)
        
        # 发送信号通知其他组件
        self.settings_visibility_changed.emit(is_visible)
        
        # 调整窗口大小以适应内容变化
        self.adjustSize()
        if self.parent():
            self.parent().adjustSize()