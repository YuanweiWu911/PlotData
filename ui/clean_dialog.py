from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QCheckBox, QComboBox, QSpinBox, QFormLayout,
                            QGroupBox, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt

class DataCleanDialog(QDialog):
    """数据清洗对话框"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        
        self.data_manager = data_manager
        
        self.setWindowTitle("数据清洗")
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建空值处理组
        na_group = QGroupBox("空值处理")
        na_layout = QVBoxLayout(na_group)
        
        # 删除空值行
        self.drop_na_check = QCheckBox("删除含有空值的行")
        na_layout.addWidget(self.drop_na_check)
        
        # 填充空值
        self.fill_na_check = QCheckBox("填充空值")
        na_layout.addWidget(self.fill_na_check)
        
        # 填充方法
        fill_method_layout = QHBoxLayout()
        fill_method_layout.addWidget(QLabel("填充方法:"))
        
        self.fill_method_combo = QComboBox()
        self.fill_method_combo.addItems(["均值", "中位数", "众数", "自定义值"])
        fill_method_layout.addWidget(self.fill_method_combo)
        
        na_layout.addLayout(fill_method_layout)
        
        # 自定义填充值
        fill_value_layout = QHBoxLayout()
        fill_value_layout.addWidget(QLabel("自定义填充值:"))
        
        self.fill_value_edit = QLineEdit("0")
        fill_value_layout.addWidget(self.fill_value_edit)
        
        na_layout.addLayout(fill_value_layout)
        
        main_layout.addWidget(na_group)
        
        # 创建重复值处理组
        dup_group = QGroupBox("重复值处理")
        dup_layout = QVBoxLayout(dup_group)
        
        # 删除重复行
        self.drop_duplicates_check = QCheckBox("删除重复行")
        dup_layout.addWidget(self.drop_duplicates_check)
        
        main_layout.addWidget(dup_group)
        
        # 创建数据转换组
        transform_group = QGroupBox("数据转换")
        transform_layout = QVBoxLayout(transform_group)
        
        # 尝试将字符串转换为数值
        self.convert_numeric_check = QCheckBox("尝试将字符串列转换为数值")
        transform_layout.addWidget(self.convert_numeric_check)
        
        # 四舍五入小数
        round_layout = QHBoxLayout()
        self.round_check = QCheckBox("四舍五入小数位数:")
        round_layout.addWidget(self.round_check)
        
        self.round_spin = QSpinBox()
        self.round_spin.setRange(0, 10)
        self.round_spin.setValue(2)
        round_layout.addWidget(self.round_spin)
        
        transform_layout.addLayout(round_layout)
        
        main_layout.addWidget(transform_group)
        
        # 创建按钮
        buttons_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.apply_cleaning)
        buttons_layout.addWidget(self.apply_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        # 连接信号
        self.fill_na_check.toggled.connect(self.toggle_fill_options)
        self.fill_method_combo.currentIndexChanged.connect(self.toggle_fill_value)
        self.round_check.toggled.connect(self.round_spin.setEnabled)
        
        # 初始状态
        self.toggle_fill_options(False)
        self.round_spin.setEnabled(False)
    
    def toggle_fill_options(self, enabled):
        """切换填充选项的启用状态"""
        self.fill_method_combo.setEnabled(enabled)
        self.toggle_fill_value(self.fill_method_combo.currentIndex())
    
    def toggle_fill_value(self, index):
        """切换自定义填充值的启用状态"""
        # 只有当选择"自定义值"且填充空值选项被勾选时才启用
        self.fill_value_edit.setEnabled(
            self.fill_na_check.isChecked() and 
            self.fill_method_combo.currentText() == "自定义值"
        )
    
    def apply_cleaning(self):
        """应用数据清洗"""
        # 收集清洗选项
        options = {
            "drop_na": self.drop_na_check.isChecked(),
            "fill_na": self.fill_na_check.isChecked(),
            "drop_duplicates": self.drop_duplicates_check.isChecked(),
            "convert_numeric": self.convert_numeric_check.isChecked(),
        }
        
        # 填充方法
        if self.fill_na_check.isChecked():
            method_text = self.fill_method_combo.currentText()
            if method_text == "均值":
                options["fill_method"] = "mean"
            elif method_text == "中位数":
                options["fill_method"] = "median"
            elif method_text == "众数":
                options["fill_method"] = "mode"
            elif method_text == "自定义值":
                options["fill_method"] = "value"
                try:
                    options["fill_value"] = float(self.fill_value_edit.text())
                except ValueError:
                    QMessageBox.warning(self, "警告", "自定义填充值必须是数字")
                    return
        
        # 四舍五入
        if self.round_check.isChecked():
            options["round_decimals"] = self.round_spin.value()
        
        # 应用清洗
        success, message = self.data_manager.clean_data(options)
        
        if success:
            QMessageBox.information(self, "成功", message)
            self.accept()
        else:
            QMessageBox.critical(self, "错误", message)