from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableView, QHeaderView, QComboBox, 
                            QGroupBox, QFormLayout, QSpinBox, QCheckBox,
                            QColorDialog, QMessageBox, QLineEdit)  # 添加缺失的QLineEdit导入
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6 import sip
from PyQt6.QtCore import QMetaObject, Qt, QThread
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSignal, QObject

import pandas as pd
import numpy as np

class PandasModel(QAbstractTableModel):
    """用于在QTableView中显示pandas DataFrame的模型"""
    
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else pd.DataFrame()
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self._data.columns)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
            
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            # 处理不同类型的数据
            if pd.isna(value):
                return ""
            elif isinstance(value, (float, np.float64)):
                return f"{value:.6g}"  # 格式化浮点数
            else:
                return str(value)
                
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(section + 1)  # 行号从1开始
        return None
    
    def update_data(self, data):
        """更新模型中的数据"""
        self.beginResetModel()
        self._data = data if data is not None else pd.DataFrame()
        self.endResetModel()


class DataView(QWidget):
    """数据视图组件"""
    
    # 修改信号定义，使其与实际使用匹配
    # 图表类型, x轴列, y轴列, 颜色, xerr, yerr, markstyle, marksize
    plot_requested = pyqtSignal(str, str, str, str, str, str, str, int)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()  # 确保初始化方法被调用
       
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建数据表视图
        self.table_label = QLabel("数据预览:")
        main_layout.addWidget(self.table_label)
        
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.verticalHeader().setVisible(True)
        
        # 创建表格模型
        self.table_model = PandasModel()
        self.table_view.setModel(self.table_model)
        
        main_layout.addWidget(self.table_view)
        
        # 创建绘图控制组
        plot_group = QGroupBox("绘图控制")
        plot_layout = QVBoxLayout(plot_group)
        
        # 创建绘图类型选择
        plot_type_layout = QHBoxLayout()
        plot_type_layout.addWidget(QLabel("绘图类型:"))
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["散点图", "带误差棒的散点图", "直方图", "2D密度图"])
        self.plot_type_combo.currentIndexChanged.connect(self.on_plot_type_changed)
        plot_type_layout.addWidget(self.plot_type_combo)

        # 标记Marker样式设置
        self.mark_style_label = QLabel("标记样式:")
        self.mark_style_combo = QComboBox()
        self.mark_style_combo.addItems(["圆形", "点", "方形", "三角", "星形"])
        
        # 标记大小设置
        self.mark_size_label = QLabel("标记大小:")
        self.mark_size_spin = QSpinBox()
        self.mark_size_spin.setRange(5, 50)
        self.mark_size_spin.setValue(20)

        # 将标记控件添加到绘图类型布局中
        plot_type_layout.addWidget(self.mark_style_label)
        plot_type_layout.addWidget(self.mark_style_combo)
        plot_type_layout.addWidget(self.mark_size_label)
        plot_type_layout.addWidget(self.mark_size_spin)

        plot_layout.addLayout(plot_type_layout)

        # 创建控制面板布局
        controls_layout = QHBoxLayout()  # 确保正确定义布局容器
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        
        # 创建数据选择表单
        form_layout = QFormLayout()
        
        # X轴数据选择
        self.x_combo = QComboBox()
        form_layout.addRow("X轴数据:", self.x_combo)
        
        # Y轴数据选择
        self.y_combo = QComboBox()
        form_layout.addRow("Y轴数据:", self.y_combo)
        
        # X轴误差数据选择（初始隐藏）
        self.xerr_combo = QComboBox()
        self.xerr_combo.addItem("无")
        self.xerr_label = QLabel("X轴误差:")
        form_layout.addRow(self.xerr_label, self.xerr_combo)
        
        # Y轴误差数据选择（初始隐藏）
        self.yerr_combo = QComboBox()
        self.yerr_combo.addItem("无")
        self.yerr_label = QLabel("Y轴误差:")
        form_layout.addRow(self.yerr_label, self.yerr_combo)
        
        # 直方图的bins设置
        self.bins_spin = QSpinBox()
        self.bins_spin.setRange(2, 100)
        self.bins_spin.setValue(10)
        self.bins_label = QLabel("分箱数量:")
        form_layout.addRow(self.bins_label, self.bins_spin)

        # 添加颜色选择组件
        self.color_button = QPushButton("选择颜色")
        self.color_button.clicked.connect(self.choose_color)
        self.selected_color = "blue"  # 默认颜色
        self.color_button.setStyleSheet(f"background-color: {self.selected_color};")
        form_layout.addRow("颜色:", self.color_button)
        plot_layout.addLayout(form_layout)
       
        # 将控件添加到布局（确认使用同一个布局对象）
        controls_layout.addWidget(QLabel("图表类型:"))
        controls_layout.addWidget(self.plot_type_combo)
        controls_layout.addWidget(self.color_button)
        
        # 新增的标记样式控件
        controls_layout.addWidget(self.mark_style_label)  # 确保使用已定义的controls_layout
        controls_layout.addWidget(self.mark_style_combo)
        controls_layout.addWidget(self.mark_size_label)
        controls_layout.addWidget(self.mark_size_spin)
        
        # 将控制面板布局添加到主布局
        main_layout.addLayout(controls_layout) 

        # 绘图按钮
        self.plot_button = QPushButton("生成图")
        self.plot_button.clicked.connect(self.request_plot)
        plot_layout.addWidget(self.plot_button)

        # 添加绘图控制组到主布局（原代码第345行附近）
        main_layout.addWidget(plot_group)  # 确保在数据筛选区域前添加        
        # 添加数据筛选区域
        filter_group = QGroupBox("数据筛选")
        filter_layout = QVBoxLayout(filter_group)
        
        # 列选择
        filter_col_layout = QHBoxLayout()
        filter_col_layout.addWidget(QLabel("筛选列:"))
        
        self.filter_col_combo = QComboBox()
        filter_col_layout.addWidget(self.filter_col_combo)
        
        filter_layout.addLayout(filter_col_layout)
        
        # 筛选条件
        filter_cond_layout = QHBoxLayout()
        
        self.filter_op_combo = QComboBox()
        self.filter_op_combo.addItems(["等于", "大于", "小于", "包含"])
        filter_cond_layout.addWidget(self.filter_op_combo)
        
        self.filter_value_edit = QLineEdit()
        filter_cond_layout.addWidget(self.filter_value_edit)
        
        filter_layout.addLayout(filter_cond_layout)
        
        # 应用筛选按钮
        self.apply_filter_button = QPushButton("应用筛选")
        self.apply_filter_button.clicked.connect(self.apply_filter)
        filter_layout.addWidget(self.apply_filter_button)
        
        # 清除筛选按钮
        self.clear_filter_button = QPushButton("清除筛选")
        self.clear_filter_button.clicked.connect(self.clear_filter)
        filter_layout.addWidget(self.clear_filter_button)
        
        main_layout.addWidget(filter_group)
        
        # 初始化UI状态
        self.on_plot_type_changed(0)  # 默认为散点图
         

    # 确保on_plot_clicked是类方法（删除嵌套定义）
    def on_plot_clicked(self):
        """处理绘图按钮点击事件"""
        try:
            # 从控件获取当前值
            plot_type = self.plot_type_combo.currentText()
            x_col = self.x_combo.currentText()
            y_col = self.y_combo.currentText()
            xerr_col = self.xerr_combo.currentText() if self.xerr_combo.currentText() != "无" else None
            yerr_col = self.yerr_combo.currentText() if self.yerr_combo.currentText() != "无" else None
            mark_style = self.mark_style_combo.currentText()
            mark_size = self.mark_size_spin.value()
     
            if not x_col or not y_col:
                QMessageBox.warning(self, "警告", "请先选择X轴和Y轴列")
                return
            
            plot_type = self.plot_type_combo.currentText()
            self.plot_requested.emit(plot_type,
                x_col,
                y_col, 
                self.selected_color,
                xerr_col,
                yerr_col,
                mark_style,
                mark_size)
 
        except Exception as e:
            print(f"绘图请求失败: {str(e)}")

    def safe_update_combobox(self):
        """安全更新下拉框的方法"""
        # 检查控件是否被删除，需要同时检查父级布局
        if sip.isdeleted(self.filter_col_combo) or not self.filter_col_combo.parent():
            self.filter_col_combo = QComboBox()
            # 获取原始布局并重新添加控件
            filter_group = self.findChild(QGroupBox, "数据筛选")
            if filter_group:
                filter_col_layout = filter_group.findChild(QHBoxLayout)
                if filter_col_layout:
                    filter_col_layout.addWidget(self.filter_col_combo)
        
        try:
            self.filter_col_combo.blockSignals(True)
            self.filter_col_combo.clear()
            if hasattr(self.data_manager, 'get_column_names'):
                columns = self.data_manager.get_column_names()
                self.filter_col_combo.addItems(columns)
            self.filter_col_combo.blockSignals(False)
        except RuntimeError as e:
            print(f"安全更新失败: {str(e)}")

    def update_data_view(self):
        """更新数据视图"""
        # 提前进行线程检查
        if not QApplication.instance().thread() == QThread.currentThread():
            QMetaObject.invokeMethod(self, "update_data_view", Qt.ConnectionType.QueuedConnection)
            return

        try:
            # 使用sip检查所有UI组件状态
            if sip.isdeleted(self):  # 检查父组件是否被删除
                return

            # 合并后的数据加载逻辑
            data = self.data_manager.get_data()
            if data is None:
                return

            # 统一更新表格模型
            self.table_model.update_data(data)
            columns = self.data_manager.get_column_names()
            
            # 安全更新所有下拉框
            self.safe_update_comboboxes(columns)
            
            # 更新标签显示
            self.table_label.setText(f"数据预览: {len(data)}行 x {len(data.columns)}列")
            
        except Exception as e:
            print(f"更新数据视图时出错: {str(e)}")

    def safe_update_comboboxes(self, columns):
        """安全更新所有下拉框"""
        combos_to_update = [
            (self.x_combo, False),
            (self.y_combo, False),
            (self.xerr_combo, True),
            (self.yerr_combo, True),
            (self.filter_col_combo, False)
        ]
        
        for combo, has_none in combos_to_update:
            if sip.isdeleted(combo):
                continue
                
            current_text = combo.currentText() if combo.count() > 0 else ""
            combo.blockSignals(True)
            combo.clear()
            
            if has_none:
                combo.addItem("无")
                
            combo.addItems(columns)
            
            if current_text in (["无"] if has_none else []) + columns:
                combo.setCurrentText(current_text)
                
            combo.blockSignals(False)
    
    def on_plot_type_changed(self, index):
        """处理绘图类型变化"""
        plot_type = self.plot_type_combo.currentText()

        # 根据绘图类型显示/隐藏相关控件
        is_scatter_plot = plot_type in ["散点图", "带误差棒的散点图"]
        
        # 标记样式和大小控件仅在散点图和带误差棒散点图时显示
        self.mark_style_label.setVisible(is_scatter_plot)
        self.mark_style_combo.setVisible(is_scatter_plot)
        self.mark_size_label.setVisible(is_scatter_plot)
        self.mark_size_spin.setVisible(is_scatter_plot)

        # 根据绘图类型显示/隐藏相关控件
        if plot_type == "散点图":
            self.y_combo.setEnabled(True)
            self.xerr_label.setVisible(False)
            self.xerr_combo.setVisible(False)
            self.yerr_label.setVisible(False)
            self.yerr_combo.setVisible(False)
            self.bins_label.setVisible(False)
            self.bins_spin.setVisible(False)
            
        elif plot_type == "带误差棒的散点图":
            self.y_combo.setEnabled(True)
            self.xerr_label.setVisible(True)
            self.xerr_combo.setVisible(True)
            self.yerr_label.setVisible(True)
            self.yerr_combo.setVisible(True)
            self.bins_label.setVisible(False)
            self.bins_spin.setVisible(False)
            
        elif plot_type == "直方图":
            self.y_combo.setEnabled(False)
            self.xerr_label.setVisible(False)
            self.xerr_combo.setVisible(False)
            self.yerr_label.setVisible(False)
            self.yerr_combo.setVisible(False)
            self.bins_label.setVisible(True)
            self.bins_spin.setVisible(True)
            
        elif plot_type == "2D密度图":
            self.y_combo.setEnabled(True)
            self.xerr_label.setVisible(False)
            self.xerr_combo.setVisible(False)
            self.yerr_label.setVisible(False)
            self.yerr_combo.setVisible(False)
            self.bins_label.setVisible(True)
            self.bins_spin.setVisible(True)
    
    def choose_color(self):
        """打开颜色选择对话框"""
        color = QColorDialog.getColor(initial=QColor(self.selected_color))
        if color.isValid():
            self.selected_color = color.name()
            self.color_button.setStyleSheet(f"background-color: {self.selected_color};")

    # 在触发绘图的代码处传递颜色参数
    def trigger_plot_action(self):
        """触发绘图动作"""
        # 需要从控件获取当前值
        plot_type = self.plot_type_combo.currentText()
        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()
        xerr_col = self.xerr_combo.currentText() if self.xerr_combo.currentText() != "无" else None
        yerr_col = self.yerr_combo.currentText() if self.yerr_combo.currentText() != "无" else None
        mark_style = self.mark_style_combo.currentText()
        mark_size = self.mark_size_spin.value()

        self.plot_requested.emit(plot_type,
            x_col,
            y_col, 
            self.selected_color,
            xerr_col,
            yerr_col,
            mark_style,
            mark_size)
 
    def request_plot(self):
        """请求绘制图表"""
        if (sip.isdeleted(self.x_combo) or 
            sip.isdeleted(self.y_combo) or
            sip.isdeleted(self.plot_type_combo)):
            return        

        # 获取当前数据（使用筛选后的数据）
        data = self.data_manager.get_data(filtered=True)

        # 获取当前选择的列和绘图类型
        x_column = self.x_combo.currentText()
        y_column = self.y_combo.currentText()
        plot_type = self.plot_type_combo.currentText()

        # 获取误差列时应排除"无"选项
        xerr_col = self.xerr_combo.currentText() if self.xerr_combo.currentText() != "无" else None
        yerr_col = self.yerr_combo.currentText() if self.yerr_combo.currentText() != "无" else None
        
        # 根据图表类型检查必要的输入
        if plot_type == "直方图":
            if not x_column:
                QMessageBox.warning(self, "警告", "请选择要绘制的X轴列")
                return
            # 直方图只需要X轴数据
            y_column = ""
        else:
            # 其他图表类型需要X轴和Y轴数据
            y_column = self.y_combo.currentText()  # 修正变量名
            if not x_column or not y_column:
                QMessageBox.warning(self, "警告", "请选择要绘制的X轴和Y轴列")
                return

        # 获取mark参数
        mark_style = self.mark_style_combo.currentText()
        mark_size = self.mark_size_spin.value()

        # 发送绘图信号
        self.plot_requested.emit(plot_type, x_column, y_column, 
            self.selected_color,
            xerr_col,
            yerr_col,
            mark_style,
            mark_size)  # 添加颜色参数        
    
    def apply_filter(self):
        """应用数据筛选"""
        column = self.filter_col_combo.currentText()
        if not column:
            QMessageBox.warning(self, "警告", "请选择筛选列")
            return
        
        operation = self.filter_op_combo.currentText()
        filter_value = self.filter_value_edit.text()
        
        if not filter_value:
            QMessageBox.warning(self, "警告", "请输入筛选值")
            return
        
        try:
            # 获取原始数据
            data = self.data_manager.get_data(filtered = False)
            
            # 根据操作类型应用不同的筛选条件
            if operation == "等于":
                try:
                    # 尝试转换为数值
                    value = float(filter_value)
                    filtered_data = data[data[column] == value]
                except ValueError:
                    # 如果不是数值，按字符串处理
                    filtered_data = data[data[column].astype(str) == filter_value]
            elif operation == "大于":
                filtered_data = data[data[column] > float(filter_value)]
            elif operation == "小于":
                filtered_data = data[data[column] < float(filter_value)]
            elif operation == "包含":
                filtered_data = data[data[column].astype(str).str.contains(filter_value, case=False)]

            # 将筛选后的数据保存到数据管理器
            self.data_manager.set_filtered_data(filtered_data)

            # 更新表格视图
            self.table_model.update_data(filtered_data)

            # 保存筛选后的数据，用于绘图
            self.data_manager.set_filtered_data(filtered_data)

            # 显示筛选结果信息
            QMessageBox.information(self, "筛选结果", 
                                   f"筛选前: {len(data)}行\n筛选后: {len(filtered_data)}行")

            # 更新状态信息
            self.table_label.setText(f"数据预览 (已筛选: {len(filtered_data)} 行)")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用筛选失败: {str(e)}")

    def clear_filter(self):
        """清除筛选条件"""
        # 恢复原始数据
        data = self.data_manager.get_data()
        self.table_model.update_data(data)

        # 清空筛选后的数据
        self.data_manager.clear_filtered_data()

        # 清空筛选输入
        self.filter_value_edit.clear()
        
        # 更新状态信息
        self.table_label.setText("数据预览")
    
    # 添加重置筛选功能
    def reset_filter(self):
        """重置数据筛选"""
        self.data_manager.reset_filter()
        # 更新表格显示原始数据
        self.table_model.update_data(self.data_manager.get_data(filtered=False))
        QMessageBox.information(self, "提示", "已重置筛选，显示所有数据")
