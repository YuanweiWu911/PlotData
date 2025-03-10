from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableView, QHeaderView, QComboBox, 
                            QGroupBox, QFormLayout, QSpinBox, QCheckBox,
                            QColorDialog, QMessageBox)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSignal
from PyQt6.QtGui import QColor

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
    
    # 自定义信号，用于请求绘图
    plot_requested = pyqtSignal(dict)
    
    def __init__(self, data_manager):
        super().__init__()
        
        self.data_manager = data_manager
        
        # 初始化UI
        self.init_ui()
    
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
        
        plot_layout.addLayout(plot_type_layout)
        
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
        
        # 颜色选择
        self.color_button = QPushButton("选择颜色")
        self.color_button.clicked.connect(self.choose_color)
        self.current_color = QColor(0, 0, 255)  # 默认蓝色
        form_layout.addRow("颜色:", self.color_button)
        
        plot_layout.addLayout(form_layout)
        
        # 绘图按钮
        self.plot_button = QPushButton("绘制图表")
        self.plot_button.clicked.connect(self.request_plot)
        plot_layout.addWidget(self.plot_button)
        
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
    
    def update_data_view(self):
        """更新数据视图"""
        data = self.data_manager.get_data()
        if data is not None:
            self.table_model.update_data(data)
            
            # 更新列选择下拉框
            columns = self.data_manager.get_column_names()
            
            # 保存当前选择
            current_x = self.x_combo.currentText() if self.x_combo.count() > 0 else ""
            current_y = self.y_combo.currentText() if self.y_combo.count() > 0 else ""
            current_xerr = self.xerr_combo.currentText() if self.xerr_combo.count() > 0 else "无"
            current_yerr = self.yerr_combo.currentText() if self.yerr_combo.count() > 0 else "无"
            
            # 更新下拉框
            self.x_combo.clear()
            self.y_combo.clear()
            self.xerr_combo.clear()
            self.yerr_combo.clear()
            
            self.xerr_combo.addItem("无")
            self.yerr_combo.addItem("无")
            
            self.x_combo.addItems(columns)
            self.y_combo.addItems(columns)
            self.xerr_combo.addItems(columns)
            self.yerr_combo.addItems(columns)
            
            # 尝试恢复之前的选择
            if current_x in columns:
                self.x_combo.setCurrentText(current_x)
            if current_y in columns:
                self.y_combo.setCurrentText(current_y)
            if current_xerr in ["无"] + columns:
                self.xerr_combo.setCurrentText(current_xerr)
            if current_yerr in ["无"] + columns:
                self.yerr_combo.setCurrentText(current_yerr)
    
    def on_plot_type_changed(self, index):
        """处理绘图类型变化"""
        plot_type = self.plot_type_combo.currentText()
        
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
        color = QColorDialog.getColor(self.current_color, self, "选择颜色")
        if color.isValid():
            self.current

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
        data = self.data_manager.get_data()
        
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
        
        # 更新表格视图
        self.table_model.update_data(filtered_data)
        
        # 更新状态信息
        self.table_label.setText(f"数据预览 (已筛选: {len(filtered_data)} 行)")
        
    except Exception as e:
        QMessageBox.critical(self, "错误", f"应用筛选失败: {str(e)}")

def clear_filter(self):
    """清除筛选条件"""
    # 恢复原始数据
    data = self.data_manager.get_data()
    self.table_model.update_data(data)
    
    # 清空筛选输入
    self.filter_value_edit.clear()
    
    # 更新状态信息
    self.table_label.setText("数据预览")