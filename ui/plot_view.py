import os
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QGroupBox, QFormLayout, QLineEdit, QApplication,
                            QMessageBox, QFileDialog, QProgressDialog, 
                            QDoubleSpinBox, QLabel, QSpinBox,
                            QComboBox, QColorDialog)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QThreadPool, QTimer
import matplotlib
from PyQt6.QtGui import QDoubleValidator, QColor
matplotlib.use('QtAgg')

# 辅助函数和常量定义
MARKER_STYLE_MAP = {
    "无标记": '',
    "圆形": 'o',
    "点": '.',
    "方形": 's',
    "三角形": '^',
    "星形": '*',
    "菱形": 'D',
    "十字": 'x',
    "加号": '+',
    "叉号": 'X'
}

# 绘图辅助类，提供参数处理和绘图相关的辅助方法
class PlotHelper:
    """绘图辅助类，提供参数处理和绘图相关的辅助方法"""
    
    @staticmethod
    def get_plot_params(plot_view):
        """从绘图视图中获取绘图参数
        
        Args:
            plot_view: 绘图视图实例
            
        Returns:
            dict: 包含绘图参数的字典
        """
        # 从控件获取当前值
        plot_type = plot_view.plot_type_combo.currentText()
        x_col = plot_view.x_combo.currentText()
        y_col = plot_view.y_combo.currentText()
        
        # 获取其他参数
        xerr_col = plot_view.xerr_combo.currentText() if plot_view.xerr_combo.currentText() != "无" else None
        yerr_col = plot_view.yerr_combo.currentText() if plot_view.yerr_combo.currentText() != "无" else None
        
        # 获取标记样式并转换为matplotlib兼容格式
        mark_style = plot_view.mark_style_combo.currentText()
        # 获取matplotlib兼容的标记样式
        matplotlib_marker = MARKER_STYLE_MAP.get(mark_style, 'o')  # 默认使用圆形
        
        mark_size = plot_view.mark_size_spin.value()
        histtype = plot_view.histtype_combo.currentText()
        bins = plot_view.bins_spin.value()
        colormap = plot_view.colorbar_combo.currentText() if plot_type == "2D密度图" else None
        
        # 获取线型
        line_style = plot_view.line_style_combo.currentText() if hasattr(plot_view, 'line_style_combo') else '-'
        line_width = plot_view.line_width_spin.value() if hasattr(plot_view, 'line_width_spin') else 2
        
        # 获取颜色
        color = plot_view.color_button.property("color")
        if not color or not isinstance(color, str):
            color = "blue"  # 默认颜色
        alpha = plot_view.alpha_spin.value()
        
        # 返回参数字典
        return {
            'plot_type': plot_type,
            'x_col': x_col,
            'y_col': y_col,
            'color': color,
            'alpha': alpha,
            'xerr_col': xerr_col,
            'yerr_col': yerr_col,
            'mark_style': matplotlib_marker,  # 使用转换后的标记样式
            'mark_size': mark_size,
            'histtype': histtype,
            'bins': bins,
            'colormap': colormap,
            'line_style': line_style,
            'line_width': line_width
        }
    
    @staticmethod
    def get_axis_settings(plot_view):
        """从绘图视图中获取坐标轴设置
        
        Args:
            plot_view: 绘图视图实例
            
        Returns:
            dict: 包含坐标轴设置的字典
        """
        # 获取标题和标签设置
        title = plot_view.title_edit.text() or None
        x_label = plot_view.x_label_edit.text() or None
        y_label = plot_view.y_label_edit.text() or None
        
        # 获取坐标轴范围设置
        try:
            x_min = float(plot_view.x_ticks_min.text()) if plot_view.x_ticks_min.text() else None
            x_max = float(plot_view.x_ticks_max.text()) if plot_view.x_ticks_max.text() else None
            y_min = float(plot_view.y_ticks_min.text()) if plot_view.y_ticks_min.text() else None
            y_max = float(plot_view.y_ticks_max.text()) if plot_view.y_ticks_max.text() else None
        except ValueError:
            x_min, x_max, y_min, y_max = None, None, None, None
            print("坐标轴范围设置格式无效，将使用自动范围")
        
        # 获取刻度和网格线设置
        x_major_ticks = plot_view.x_major_ticks_spin.value()
        x_minor_ticks = plot_view.x_minor_ticks_spin.value()
        x_show_grid = plot_view.x_grid_checkbox.isChecked()
        y_major_ticks = plot_view.y_major_ticks_spin.value()
        y_minor_ticks = plot_view.y_minor_ticks_spin.value()
        y_show_grid = plot_view.y_grid_checkbox.isChecked()
        
        return {
            'title': title,
            'x_label': x_label,
            'y_label': y_label,
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
    
    @staticmethod
    def validate_plot_request(data, plot_type, x_col, y_col, xerr_col=None, yerr_col=None):
        """验证绘图请求参数
        
        Args:
            data: 数据
            plot_type: 绘图类型
            x_col: X轴列名
            y_col: Y轴列名
            xerr_col: X误差列名
            yerr_col: Y误差列名
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if data is None or data.empty:
            return False, "没有可用的数据"
            
        # 检查列是否存在
        if x_col not in data.columns:
            return False, f"X轴列 '{x_col}' 不存在"
            
        if y_col not in data.columns and plot_type != "直方图":
            return False, f"Y轴列 '{y_col}' 不存在"
            
        # 检查误差棒列
        if xerr_col and xerr_col not in data.columns:
            return False, f"X误差列 '{xerr_col}' 不存在"
            
        if yerr_col and yerr_col not in data.columns:
            return False, f"Y误差列 '{yerr_col}' 不存在"
            
        return True, ""

class UIHelper:
    """UI辅助类，提供创建UI元素的静态方法"""
    
    @staticmethod
    def create_button(text, icon=None, slot=None, checkable=False, checked=False, tooltip=None, fixed_width=None):
        """创建按钮的辅助方法"""
        button = QPushButton(text)
        if icon:
            button.setIcon(icon)
        if slot:
            button.clicked.connect(slot)
        if checkable:
            button.setCheckable(True)
            button.setChecked(checked)
        if tooltip:
            button.setToolTip(tooltip)
        if fixed_width:
            button.setFixedWidth(fixed_width)
        return button
    
    @staticmethod
    def create_spin_box(min_val, max_val, default_val, step=1, tooltip=None, suffix=None):
        """创建数字输入框的辅助方法"""
        spin_box = QSpinBox()
        spin_box.setRange(min_val, max_val)
        spin_box.setValue(default_val)
        spin_box.setSingleStep(step)
        if tooltip:
            spin_box.setToolTip(tooltip)
        if suffix:
            spin_box.setSuffix(suffix)
        return spin_box
    
    @staticmethod
    def create_double_spin_box(min_val, max_val, default_val, step=0.1, decimals=1, tooltip=None):
        """创建浮点数输入框的辅助方法"""
        spin_box = QDoubleSpinBox()
        spin_box.setRange(min_val, max_val)
        spin_box.setValue(default_val)
        spin_box.setSingleStep(step)
        spin_box.setDecimals(decimals)
        if tooltip:
            spin_box.setToolTip(tooltip)
        return spin_box
    
    @staticmethod
    def create_combo_box(items, current_index=0, slot=None, tooltip=None):
        """创建下拉框的辅助方法"""
        combo_box = QComboBox()
        combo_box.addItems(items)
        combo_box.setCurrentIndex(current_index)
        if slot:
            combo_box.currentIndexChanged.connect(slot)
        if tooltip:
            combo_box.setToolTip(tooltip)
        return combo_box
    
    @staticmethod
    def create_line_edit(placeholder=None, validator=None, tooltip=None):
        """创建文本输入框的辅助方法"""
        line_edit = QLineEdit()
        if placeholder:
            line_edit.setPlaceholderText(placeholder)
        if validator:
            line_edit.setValidator(validator)
        if tooltip:
            line_edit.setToolTip(tooltip)
        return line_edit
    
    @staticmethod
    def add_widgets_to_layout(layout, widgets_with_labels):
        """向布局中添加带标签的控件
        
        Args:
            layout: 要添加到的布局
            widgets_with_labels: 列表，每个元素是(label_text, widget)元组
        """
        for label_text, widget in widgets_with_labels:
            if label_text:
                layout.addWidget(QLabel(label_text))
            layout.addWidget(widget)
    
    @staticmethod
    def create_container_with_layout(layout_type=QHBoxLayout, margin=0):
        """创建带有指定布局的容器控件"""
        container = QWidget()
        layout = layout_type(container)
        layout.setContentsMargins(margin, margin, margin, margin)
        return container, layout

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
        
        # 初始化线程池
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(4)  # 设置最大线程数
        
        # 初始化防抖动定时器
#       from PyQt6.QtCore import QTimer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)  # 设置为单次触发
        self.debounce_timer.setInterval(300)    # 设置防抖动间隔为300毫秒
        self.debounce_timer.timeout.connect(self._execute_plot_request)
        
        # 存储当前绘图请求参数
        self.current_request = None
        self.current_plot_params = None  # 初始化current_plot_params属性
        
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
        
        # 使用辅助方法创建工具栏按钮
        self.toggle_settings_button = UIHelper.create_button(
            "绘图设置", 
            icon=self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView),
            slot=self.toggle_settings_visibility,
            checkable=True,
            checked=True
        )
        toolbar_layout.addWidget(self.toggle_settings_button)
        
        self.save_settings_toolbar_button = UIHelper.create_button(
            "保存设置", 
            icon=self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton),
            slot=self.save_plot_settings
        )
        toolbar_layout.addWidget(self.save_settings_toolbar_button)
        
        self.load_settings_toolbar_button = UIHelper.create_button(
            "加载设置", 
            icon=self.style().standardIcon(self.style().StandardPixmap.SP_DialogOpenButton),
            slot=self.load_plot_settings
        )
        toolbar_layout.addWidget(self.load_settings_toolbar_button)
        
        self.save_plot_toolbar_button = UIHelper.create_button(
            "保存图表", 
            icon=self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton),
            slot=self.save_plot
        )
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
        self.settings_group = QGroupBox("绘图设置")
        settings_layout = QFormLayout(self.settings_group)
        
        # 创建绘图控制区域
        plot_control_layout = QVBoxLayout()

        # 样式设置
        style_layout = QHBoxLayout()

        # 绘图类型选择
        self.plot_type_combo = UIHelper.create_combo_box(
            ["散点图", "带误差棒的散点图", "直方图", "2D密度图", "线图"],
            slot=self.on_plot_type_changed
        )
        UIHelper.add_widgets_to_layout(style_layout, [("绘图类型:", self.plot_type_combo)])
        
        # 颜色选择
        self.color_button = UIHelper.create_button(
            "颜色选择", 
            slot=self.choose_color, 
            fixed_width=60
        )
        self.color_button.setStyleSheet("background-color: blue;")
        self.color_button.setProperty("color", "blue")  # 存储颜色值
        UIHelper.add_widgets_to_layout(style_layout, [("", self.color_button)])

        # 添加透明度设置控件
        self.alpha_spin = UIHelper.create_double_spin_box(
            0.1, 1.0, 0.7, 0.1, 1, 
            tooltip="设置图形的透明度"
        )
        UIHelper.add_widgets_to_layout(style_layout, [("透明度", self.alpha_spin)])

        # 标记样式
        self.mark_style_combo = UIHelper.create_combo_box(
            ["圆形", "点", "方形", "三角形", "星形", "菱形", "十字", "加号", "叉号"]
        )
        UIHelper.add_widgets_to_layout(style_layout, [("Marker样式", self.mark_style_combo)])
        
        # 标记大小
        self.mark_size_spin = UIHelper.create_spin_box(1, 30, 10)
        UIHelper.add_widgets_to_layout(style_layout, [("Marker大小", self.mark_size_spin)])
        
        # 线型设置
        self.line_style_combo = UIHelper.create_combo_box(["-", "--", ":", "-."])
        UIHelper.add_widgets_to_layout(style_layout, [("线型", self.line_style_combo)])

        # 添加线宽设置
        self.line_width_spin = UIHelper.create_spin_box(1, 10, 2)
        UIHelper.add_widgets_to_layout(style_layout, [("线宽", self.line_width_spin)])

        plot_control_layout.addLayout(style_layout)
       
        # 数据列选择
        columns_container, columns_layout = UIHelper.create_container_with_layout()
        
        # X轴列选择
        self.x_combo = UIHelper.create_combo_box([])
        UIHelper.add_widgets_to_layout(columns_layout, [("X轴数据:", self.x_combo)])
        
        # Y轴列选择
        self.y_combo = UIHelper.create_combo_box([])
        UIHelper.add_widgets_to_layout(columns_layout, [("Y轴数据:", self.y_combo)])
        
        plot_control_layout.addWidget(columns_container)

        # 误差棒列选择
        self.error_settings, error_layout = UIHelper.create_container_with_layout()
        
        self.xerr_combo = UIHelper.create_combo_box([])
        UIHelper.add_widgets_to_layout(error_layout, [("X轴误差:", self.xerr_combo)])
        
        self.yerr_combo = UIHelper.create_combo_box([])
        UIHelper.add_widgets_to_layout(error_layout, [("Y轴误差:", self.yerr_combo)])
        
        plot_control_layout.addWidget(self.error_settings)
        
        # 直方图特有设置
        self.hist_settings, hist_layout = UIHelper.create_container_with_layout()
        
        self.histtype_combo = UIHelper.create_combo_box(["bar", "barstacked", "step", "stepfilled"])
        UIHelper.add_widgets_to_layout(hist_layout, [("直方图类型:", self.histtype_combo)])
        
        self.bins_spin = UIHelper.create_spin_box(5, 200, 50)
        UIHelper.add_widgets_to_layout(hist_layout, [("分箱数:", self.bins_spin)])
        
        self.hist_settings.setVisible(False)  # 默认隐藏
        plot_control_layout.addWidget(self.hist_settings)
        
        # 2D密度图特有设置
        self.density_settings, density_layout = UIHelper.create_container_with_layout()
        
        colormap_options = ["viridis", "plasma", "inferno", "magma", "cividis", 
                          "Greys", "Purples", "Blues", "Greens", "Oranges", "Reds",
                          "YlOrBr", "YlOrRd", "OrRd", "PuRd", "RdPu", "BuPu",
                          "GnBu", "PuBu", "YlGnBu", "PuBuGn", "BuGn", "YlGn",
                          "jet", "turbo", "rainbow", "coolwarm", "bwr", "seismic"]
        self.colorbar_combo = UIHelper.create_combo_box(colormap_options)
        UIHelper.add_widgets_to_layout(density_layout, [("颜色映射:", self.colorbar_combo)])
        
        self.density_bins_spin = UIHelper.create_spin_box(10, 500, 100)
        UIHelper.add_widgets_to_layout(density_layout, [("分辨率:", self.density_bins_spin)])
        
        self.density_settings.setVisible(False)  # 默认隐藏
        plot_control_layout.addWidget(self.density_settings)
        settings_layout.addRow("", plot_control_layout)
        
        # 标题设置
        self.title_edit = UIHelper.create_line_edit(placeholder="标题:")
        settings_layout.addRow("", self.title_edit)
        
        # 添加X轴刻度设置
        x_ticks_layout = QHBoxLayout()
       
        # X轴标签设置
        self.x_label_edit = UIHelper.create_line_edit(placeholder="X轴标签:")
        self.x_ticks_min = UIHelper.create_line_edit(
            placeholder="X轴最小值（支持科学计数法）",
            validator=QDoubleValidator(notation=QDoubleValidator.Notation.ScientificNotation)
        )
        
        x_ticks_layout.addWidget(self.x_label_edit)
        x_ticks_layout.addWidget(QLabel("X轴范围:"))
        x_ticks_layout.addWidget(self.x_ticks_min)

        self.x_ticks_max = UIHelper.create_line_edit(
            placeholder="X轴最大值",
            validator=QDoubleValidator(notation=QDoubleValidator.Notation.ScientificNotation)
        )
        x_ticks_layout.addWidget(QLabel("-"))
        x_ticks_layout.addWidget(self.x_ticks_max)
        
        settings_layout.addRow("", x_ticks_layout)
        
        # 添加Y轴刻度设置
        y_ticks_layout = QHBoxLayout()
        
        # Y轴标签设置
        self.y_label_edit = UIHelper.create_line_edit(placeholder="Y轴标签:")
        self.y_ticks_min = UIHelper.create_line_edit(
            placeholder="Y轴最小值（支持科学计数法）",
            validator=QDoubleValidator(notation=QDoubleValidator.Notation.ScientificNotation)
        )
        
        y_ticks_layout.addWidget(self.y_label_edit)
        y_ticks_layout.addWidget(QLabel("Y轴范围:"))
        y_ticks_layout.addWidget(self.y_ticks_min)

        self.y_ticks_max = UIHelper.create_line_edit(
            placeholder="Y轴最大值",
            validator=QDoubleValidator(notation=QDoubleValidator.Notation.ScientificNotation)
        )
        y_ticks_layout.addWidget(QLabel("-"))
        y_ticks_layout.addWidget(self.y_ticks_max)
 
        settings_layout.addRow("", y_ticks_layout)

        # 坐标轴刻度设置
        ticks_layout = QHBoxLayout()

        ticks_layout.addWidget(QLabel("x_majorticks:"))
        self.x_major_ticks_spin = QSpinBox()
        self.x_major_ticks_spin.setRange(0, 20)
        self.x_major_ticks_spin.setValue(5)
        ticks_layout.addWidget(self.x_major_ticks_spin)

        ticks_layout.addWidget(QLabel("x_minorticks:"))
        self.x_minor_ticks_spin = QSpinBox()
        self.x_minor_ticks_spin.setRange(0, 10)
        self.x_minor_ticks_spin.setValue(1)
        ticks_layout.addWidget(self.x_minor_ticks_spin)

        ticks_layout.addWidget(QLabel("y_majorticks:"))
        self.y_major_ticks_spin = QSpinBox()
        self.y_major_ticks_spin.setRange(0, 20)
        self.y_major_ticks_spin.setValue(5)
        ticks_layout.addWidget(self.y_major_ticks_spin)
#       UIHelper.add_widgets_to_layout(ticks_layout,[("Y轴主刻度:", self.y_major_ticks_spin)])

        ticks_layout.addWidget(QLabel("y_minorticks:"))
        self.y_minor_ticks_spin = QSpinBox()
        self.y_minor_ticks_spin.setRange(0, 10)
        self.y_minor_ticks_spin.setValue(1)
        ticks_layout.addWidget(self.y_minor_ticks_spin)
        settings_layout.addRow("",ticks_layout)
#       UIHelper.add_widgets_to_layout(ticks_layout,[("Y轴主刻度:", self.x_minor_ticks_spin)])

#       axis_group_layout.addWidget(ticks_group)
    @pyqtSlot()  # 修改装饰器，移除dict参数
    def apply_settings(self):
        """应用新的图表设置"""
        if not self.current_plot_params:
            QMessageBox.information(self, "提示", "请先生成图表后再应用设置")
            return
        
        # 使用PlotHelper获取坐标轴设置
        axis_settings = PlotHelper.get_axis_settings(self)
        
        # 更新当前参数中的设置
        self.current_plot_params.update(axis_settings)
        
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
            self.current_plot_params.get('histtype', 'bar'),
            self.current_plot_params.get('bins', 10),
            self.current_plot_params.get('colormap', 'viridis'),
            self.current_plot_params.get('line_style', '-'),
            self.current_plot_params.get('line_width', 2)            
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
        
        # 使用PlotHelper获取绘图参数和坐标轴设置
        plot_params = PlotHelper.get_plot_params(self)
        axis_settings = PlotHelper.get_axis_settings(self)
        
        # 提取需要保存的设置
        settings = {
            # 数据文件信息
            'data_file_path': current_file_path,
            # 数据筛选参数
            'filter_expr': data_view.filter_expr_edit.toPlainText() if data_view else ''
        }
        
        # 合并绘图参数和坐标轴设置
        settings.update(plot_params)
        settings.update(axis_settings)
        
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
            self.alpha_spin.setValue(settings.get('alpha', 0.7))  #透明度
            
            # 设置其他参数
            self.plot_type_combo.setCurrentText(settings.get('plot_type', '散点图'))
            self.mark_style_combo.setCurrentText(settings.get('mark_style', 'o'))
            self.mark_size_spin.setValue(settings.get('mark_size', 10))

            # 设置线型和线宽
            if hasattr(self, 'line_style_combo'):
                line_style = settings.get('line_style', '-')
                index = self.line_style_combo.findText(line_style)
                if index >= 0:
                    self.line_style_combo.setCurrentIndex(index)
            if hasattr(self, 'line_width_spin'):
                self.line_width_spin.setValue(settings.get('line_width', 2))        

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
    def handle_plot_request(self, plot_type, 
        x_col, y_col, color, xerr_col=None, yerr_col=None, 
        mark_style='o', mark_size=10, histtype='bar', 
        bins=50, colormap='viridis', line_style='-',
        line_width=2, alpha=0.7):
        """处理绘图请求，使用工作线程进行绘图操作"""
        # 保存当前绘图参数
        self.current_plot_params = {
            'plot_type': plot_type,
            'x_col': x_col,
            'y_col': y_col,
            'color': color,
            'alpha': alpha,
            'xerr_col': xerr_col,
            'yerr_col': yerr_col,
            'mark_style': mark_style,
            'mark_size': mark_size,
            'histtype': histtype,
            'bins': bins,
            'colormap': colormap,
            'line_style': line_style,
            'line_width': line_width
        }        

        # 获取数据
        data = self.data_manager.get_data()
        
        # 验证绘图请求参数
        is_valid, error_message = PlotHelper.validate_plot_request(
            data, plot_type, x_col, y_col, xerr_col, yerr_col
        )
        
        if not is_valid:
            QMessageBox.warning(self, "错误", error_message)
            return
        
        try:
            # 获取坐标轴设置
            axis_settings = PlotHelper.get_axis_settings(self)
            
            # 提取设置值
            title = axis_settings['title']
            x_label = axis_settings['x_label']
            y_label = axis_settings['y_label']
            x_min = axis_settings['x_min']
            x_max = axis_settings['x_max']
            y_min = axis_settings['y_min']
            y_max = axis_settings['y_max']
            x_major_ticks = axis_settings['x_major_ticks']
            x_minor_ticks = axis_settings['x_minor_ticks']
            x_show_grid = axis_settings['x_show_grid']
            y_major_ticks = axis_settings['y_major_ticks']
            y_minor_ticks = axis_settings['y_minor_ticks']
            y_show_grid = axis_settings['y_show_grid']
            
            # 创建绘图工作线程
            from core.plot_worker import PlotWorker
            
            # 创建工作线程
            worker = PlotWorker(
                self.visualizer,
                plot_type,
                data,
                x_col=x_col,
                y_col=y_col,
                xerr_col=xerr_col,
                yerr_col=yerr_col,
                color=color,
                mark_style=mark_style,
                mark_size=mark_size,
                histtype=histtype,
                bins=bins,
                colormap=colormap,
                title=title,
                x_label=x_label,
                y_label=y_label,
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                x_major_ticks=x_major_ticks,
                x_minor_ticks=x_minor_ticks,
                x_show_grid=x_show_grid,
                y_major_ticks=y_major_ticks,
                y_minor_ticks=y_minor_ticks,
                y_show_grid=y_show_grid,
                alpha=alpha,  # 默认透明度
                line_style = line_style,
                line_width = line_width
            )
            
            # 连接信号
            worker.signals.finished.connect(self._on_plot_finished)
            worker.signals.error.connect(self._on_plot_error)
            
            # 启动工作线程
            self.thread_pool.start(worker)
            
            print(f"绘图请求已提交到工作线程: {plot_type}")
            
        except Exception as e:
            QMessageBox.critical(self, "绘图错误", f"绘图过程中发生错误:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def _on_plot_finished(self, success, message):
        """绘图完成回调函数"""
        if success:
            print(f"绘图成功: {message}")
        else:
            QMessageBox.warning(self, "绘图警告", f"绘图过程中发生问题:\n{message}")
    
    def _on_plot_error(self, error_message):
        """绘图错误回调函数"""
        QMessageBox.critical(self, "绘图错误", f"绘图过程中发生错误:\n{error_message}")
        import traceback
        traceback.print_exc()

    def update_columns(self):
        """更新列选择下拉框"""
        # 保存当前选择的值
        current_x = self.x_combo.currentText() if self.x_combo.count() > 0 else ""
        current_y = self.y_combo.currentText() if self.y_combo.count() > 0 else ""
        current_xerr = self.xerr_combo.currentText() if self.xerr_combo.count() > 0 else ""
        current_yerr = self.yerr_combo.currentText() if self.yerr_combo.count() > 0 else ""
        
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
            print("没有可用的数据列")
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
            
        print(f"更新列完成，可用列: {columns}")

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
            # 隐藏Y轴数据选择控件，但保留Y轴标签
            self.y_combo.setVisible(False)
            # 找到Y轴数据标签并保持其可见
            for i in range(self.y_combo.parentWidget().layout().count()):
                item = self.y_combo.parentWidget().layout().itemAt(i)
                if item.widget() and isinstance(item.widget(), QLabel) and item.widget().text() == "Y轴数据:":
                    item.widget().setVisible(False)
                    break
        else:
            # 对于其他图表类型，显示Y轴数据选择控件
            self.y_combo.setVisible(True)
            # 显示Y轴数据标签
            for i in range(self.y_combo.parentWidget().layout().count()):
                item = self.y_combo.parentWidget().layout().itemAt(i)
                if item.widget() and isinstance(item.widget(), QLabel) and item.widget().text() == "Y轴数据:":
                    item.widget().setVisible(True)
                    break
            
        if plot_type == "2D密度图":
            self.density_settings.setVisible(True)
        elif plot_type == "带误差棒的散点图":
            self.error_settings.setVisible(True)

        # 更新标记样式下拉框选项
        self.update_marker_styles()
        
        print(f"绘图类型已更改为: {plot_type}")
    
    def update_marker_styles(self):
        """根据绘图类型更新标记样式选项"""
        current_style = self.mark_style_combo.currentText()
        self.mark_style_combo.clear()
        
        # 添加标记样式选项，使用全局定义的MARKER_STYLE_MAP的键
        marker_styles = list(MARKER_STYLE_MAP.keys())
        self.mark_style_combo.addItems(marker_styles)
        
        # 尝试恢复之前的选择
        if current_style in marker_styles:
            self.mark_style_combo.setCurrentText(current_style)
        else:
            self.mark_style_combo.setCurrentIndex(0)  # 默认选择第一个样式
    
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
        """处理绘图请求，使用防抖动机制"""
        # 如果定时器已经在运行，重置它
        if self.debounce_timer.isActive():
            self.debounce_timer.stop()
        
        try:
            print("PlotView 接收到绘图请求")
            
            # 获取数据
            data = self.data_manager.get_data()
            
            # 获取绘图参数
            plot_params = PlotHelper.get_plot_params(self)
            
            # 验证绘图请求参数
            is_valid, error_message = PlotHelper.validate_plot_request(
                data, 
                plot_params['plot_type'], 
                plot_params['x_col'], 
                plot_params['y_col'], 
                plot_params['xerr_col'], 
                plot_params['yerr_col']
            )
            
            if not is_valid:
                QMessageBox.warning(self, "错误", error_message)
                return
            
            # 准备绘图参数
            self._prepare_plot_request()
            
            # 获取当前请求中的参数用于日志输出
            plot_type = self.current_request['plot_type']
            x_col = self.current_request['x_col']
            y_col = self.current_request['y_col']
            mark_style = self.current_request['mark_style']
            color = self.current_request['color']
                
            print(f"准备绘图: 类型={plot_type}, X={x_col}, Y={y_col}, 颜色={color}, 标记样式={mark_style}")
            
            # 启动定时器，防抖动处理
            self.debounce_timer.start()
            
        except Exception as e:
            print(f"绘图请求处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"绘图请求处理失败: {str(e)}")

    def _prepare_plot_request(self):
        """准备绘图请求参数"""
        # 使用PlotHelper获取绘图参数
        self.current_request = PlotHelper.get_plot_params(self)

    def _execute_plot_request(self):
        """实际执行绘图请求，由防抖动定时器触发"""
        if not self.current_request:
            return
            
        try:
            # 防止重复调用
            if hasattr(self, '_is_plotting') and self._is_plotting:
                print("绘图正在进行中，请稍候...")
                return
                
            self._is_plotting = True
            
            # 从当前请求中获取所有参数
            params = self.current_request
            
            # 调用绘图方法
            self.handle_plot_request(
                params['plot_type'], 
                params['x_col'], 
                params['y_col'], 
                params['color'], 
                params['xerr_col'], 
                params['yerr_col'], 
                params['mark_style'], 
                params['mark_size'], 
                params['histtype'], 
                params['bins'], 
                params['colormap'],
                params['line_style'], 
                params['line_width'], 
                params['alpha']
            )
            
            print(f"绘图请求处理完成")
            
        except Exception as e:
            print(f"绘图请求处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"绘图请求处理失败: {str(e)}")
        finally:
            # 无论成功还是失败，都重置绘图状态
            self._is_plotting = False

    # 确保方法名称与信号连接中使用的名称一致
    def toggle_settings_visibility(self):
        """切换设置区域的显示状态"""
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

        # 更新按钮文本
        self.toggle_settings_button.setText("绘图设置 ✓" if is_visible else "绘图设置")
        
        # 设置按钮背景色
        if is_visible:
            self.toggle_settings_button.setStyleSheet("background-color: #4CAF50;")
        else:
            self.toggle_settings_button.setStyleSheet("")



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
            # 隐藏Y轴数据选择控件，但保留Y轴标签
            self.y_combo.setVisible(False)
            # 找到Y轴数据标签并保持其可见
            for i in range(self.y_combo.parentWidget().layout().count()):
                item = self.y_combo.parentWidget().layout().itemAt(i)
                if item.widget() and isinstance(item.widget(), QLabel) and item.widget().text() == "Y轴数据:":
                    item.widget().setVisible(False)
                    break
        else:
            # 对于其他图表类型，显示Y轴数据选择控件
            self.y_combo.setVisible(True)
            # 显示Y轴数据标签
            for i in range(self.y_combo.parentWidget().layout().count()):
                item = self.y_combo.parentWidget().layout().itemAt(i)
                if item.widget() and isinstance(item.widget(), QLabel) and item.widget().text() == "Y轴数据:":
                    item.widget().setVisible(True)
                    break
            
        if plot_type == "2D密度图":
            self.density_settings.setVisible(True)
        elif plot_type == "带误差棒的散点图":
            self.error_settings.setVisible(True)