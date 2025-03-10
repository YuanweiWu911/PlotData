from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                            QGroupBox, QHeaderView)
from PyQt6.QtCore import Qt

class StatsView(QWidget):
    """数据统计视图组件"""
    
    def __init__(self, data_manager):
        super().__init__()
        
        self.data_manager = data_manager
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建列选择区域
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("选择列:"))
        
        self.column_combo = QComboBox()
        self.column_combo.addItem("所有数值列")
        select_layout.addWidget(self.column_combo)
        
        self.refresh_button = QPushButton("刷新统计")
        self.refresh_button.clicked.connect(self.update_statistics)
        select_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(select_layout)
        
        # 创建统计表格
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["统计量", "值"])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        main_layout.addWidget(self.stats_table)
    
    def update_columns(self):
        """更新列选择下拉框"""
        self.column_combo.clear()
        self.column_combo.addItem("所有数值列")
        
        columns = self.data_manager.get_column_names()
        if columns:
            self.column_combo.addItems(columns)
    
    def update_statistics(self):
        """更新统计信息"""
        selected = self.column_combo.currentText()
        
        if selected == "所有数值列":
            column = None
        else:
            column = selected
        
        stats = self.data_manager.get_statistics(column)
        
        if not stats:
            self.stats_table.setRowCount(1)
            self.stats_table.setItem(0, 0, QTableWidgetItem("错误"))
            self.stats_table.setItem(0, 1, QTableWidgetItem("无法获取统计信息"))
            return
        
        if "error" in stats:
            self.stats_table.setRowCount(1)
            self.stats_table.setItem(0, 0, QTableWidgetItem("错误"))
            self.stats_table.setItem(0, 1, QTableWidgetItem(stats["error"]))
            return
        
        # 清空表格
        self.stats_table.setRowCount(0)
        
        # 填充统计信息
        if column:
            # 单列统计
            row = 0
            for key, value in stats.items():
                if key == "四分位数" and isinstance(value, dict):
                    # 处理四分位数
                    for q_key, q_value in value.items():
                        self.stats_table.insertRow(row)
                        self.stats_table.setItem(row, 0, QTableWidgetItem(f"四分位数 {q_key}"))
                        self.stats_table.setItem(row, 1, QTableWidgetItem(str(q_value)))
                        row += 1
                else:
                    self.stats_table.insertRow(row)
                    self.stats_table.setItem(row, 0, QTableWidgetItem(str(key)))
                    self.stats_table.setItem(row, 1, QTableWidgetItem(str(value)))
                    row += 1
        else:
            # 多列统计
            for col, col_stats in stats.items():
                # 添加列名作为分隔行
                self.stats_table.insertRow(self.stats_table.rowCount())
                header_item = QTableWidgetItem(col)
                header_item.setBackground(Qt.GlobalColor.lightGray)
                self.stats_table.setItem(self.stats_table.rowCount()-1, 0, header_item)
                self.stats_table.setItem(self.stats_table.rowCount()-1, 1, QTableWidgetItem(""))
                
                # 添加该列的统计数据
                for stat_name, stat_value in col_stats.items():
                    self.stats_table.insertRow(self.stats_table.rowCount())
                    self.stats_table.setItem(self.stats_table.rowCount()-1, 0, QTableWidgetItem(str(stat_name)))
                    self.stats_table.setItem(self.stats_table.rowCount()-1, 1, QTableWidgetItem(str(stat_value)))