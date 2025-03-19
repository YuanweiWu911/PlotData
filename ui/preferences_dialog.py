from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTabWidget, QWidget, QCheckBox, 
                            QComboBox, QSpinBox, QFormLayout, QGroupBox,
                            QMessageBox, QColorDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class PreferencesDialog(QDialog):
    """首选项对话框"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        
        self.setWindowTitle("首选项")
        self.setMinimumWidth(500)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 常规选项卡
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # 主题设置
        theme_group = QGroupBox("主题")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色", "深色"])
        theme_layout.addRow("应用主题:", self.theme_combo)
        
        general_layout.addWidget(theme_group)
        
        # 最近文件设置
        recent_group = QGroupBox("最近文件")
        recent_layout = QFormLayout(recent_group)
        
        self.max_recent_spin = QSpinBox()
        self.max_recent_spin.setRange(0, 30)
        recent_layout.addRow("最大记录数:", self.max_recent_spin)
        
        self.clear_recent_button = QPushButton("清除最近文件记录")
        self.clear_recent_button.clicked.connect(self.clear_recent_files)
        recent_layout.addRow("", self.clear_recent_button)
        
        general_layout.addWidget(recent_group)
        
        # 自动保存设置
        self.auto_save_check = QCheckBox("自动保存设置")
        general_layout.addWidget(self.auto_save_check)
        
        self.tab_widget.addTab(general_tab, "常规")
        
        # 图表选项卡
        plot_tab = QWidget()
        plot_layout = QVBoxLayout(plot_tab)
        
        # 默认图表设置
        plot_group = QGroupBox("默认图表设置")
        plot_form = QFormLayout(plot_group)
        
        self.default_plot_combo = QComboBox()
        self.default_plot_combo.addItems(["散点图", "折线图", "柱状图", "饼图", "直方图"])
        plot_form.addRow("默认图表类型:", self.default_plot_combo)
        
        self.default_color_button = QPushButton()
        self.default_color_button.setFixedWidth(80)
        self.default_color_button.clicked.connect(self.choose_color)
        plot_form.addRow("默认颜色:", self.default_color_button)
        
        self.default_dpi_spin = QSpinBox()
        self.default_dpi_spin.setRange(72, 600)
        plot_form.addRow("默认DPI:", self.default_dpi_spin)
        
        self.show_grid_check = QCheckBox()
        plot_form.addRow("显示网格:", self.show_grid_check)
        
        plot_layout.addWidget(plot_group)
        
        # 数据显示设置
        data_group = QGroupBox("数据显示设置")
        data_form = QFormLayout(data_group)
        
        self.decimal_places_spin = QSpinBox()
        self.decimal_places_spin.setRange(0, 10)
        data_form.addRow("小数位数:", self.decimal_places_spin)
        
        plot_layout.addWidget(data_group)
        
        self.tab_widget.addTab(plot_tab, "图表")
        
        main_layout.addWidget(self.tab_widget)
        
        # 创建按钮
        buttons_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("重置为默认")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        buttons_layout.addWidget(self.reset_button)
        
        buttons_layout.addStretch()
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.apply_settings)
        buttons_layout.addWidget(self.apply_button)
        
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.save_and_close)
        self.ok_button.setDefault(True)
        buttons_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_settings(self):
        """从配置加载设置"""
        # 主题
        theme = self.config_manager.get("theme", "light")
        self.theme_combo.setCurrentText("深色" if theme == "dark" else "浅色")
        
        # 最近文件
        max_recent = self.config_manager.get("max_recent_files", 10)
        self.max_recent_spin.setValue(max_recent)
        
        # 自动保存
        auto_save = self.config_manager.get("auto_save_settings", False)
        self.auto_save_check.setChecked(auto_save)
        
        # 默认图表类型
        default_plot = self.config_manager.get("default_plot_type", "散点图")
        self.default_plot_combo.setCurrentText(default_plot)
        
        # 默认颜色
        default_color = self.config_manager.get("default_plot_color", "blue")
        self.set_color_button(default_color)
        
        # 默认DPI
        default_dpi = self.config_manager.get("default_dpi", 300)
        self.default_dpi_spin.setValue(default_dpi)
        
        # 显示网格
        show_grid = self.config_manager.get("show_grid", True)
        self.show_grid_check.setChecked(show_grid)
        
        # 小数位数
        decimal_places = self.config_manager.get("decimal_places", 2)
        self.decimal_places_spin.setValue(decimal_places)
    
    def set_color_button(self, color_name):
        """设置颜色按钮的背景色"""
        color = QColor(color_name)
        self.default_color_button.setStyleSheet(
            f"background-color: {color.name()}; color: {'white' if color.lightness() < 128 else 'black'};"
        )
        self.default_color_button.setText(color.name())
    
    def choose_color(self):
        """打开颜色选择对话框"""
        current_color = QColor(self.default_color_button.text())
        color = QColorDialog.getColor(current_color, self, "选择默认图表颜色")
        
        if color.isValid():
            self.set_color_button(color.name())
    
    def clear_recent_files(self):
        """清除最近文件记录"""
        reply = QMessageBox.question(
            self, "确认", "确定要清除所有最近文件记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.set("recent_files", [])
            QMessageBox.information(self, "成功", "最近文件记录已清除")
    
    def apply_settings(self):
        """应用设置但不关闭对话框"""
        # 主题
        theme = "dark" if self.theme_combo.currentText() == "深色" else "light"
        self.config_manager.set("theme", theme)
        
        # 最近文件
        max_recent = self.max_recent_spin.value()
        self.config_manager.set("max_recent_files", max_recent)
        
        # 自动保存
        auto_save = self.auto_save_check.isChecked()
        self.config_manager.set("auto_save_settings", auto_save)
        
        # 默认图表类型
        default_plot = self.default_plot_combo.currentText()
        self.config_manager.set("default_plot_type", default_plot)
        
        # 默认颜色
        default_color = self.default_color_button.text()
        self.config_manager.set("default_plot_color", default_color)
        
        # 默认DPI
        default_dpi = self.default_dpi_spin.value()
        self.config_manager.set("default_dpi", default_dpi)
        
        # 显示网格
        show_grid = self.show_grid_check.isChecked()
        self.config_manager.set("show_grid", show_grid)
        
        # 小数位数
        decimal_places = self.decimal_places_spin.value()
        self.config_manager.set("decimal_places", decimal_places)
        
        # 保存配置
        self.config_manager.save_config()
        
        # 通知用户
        QMessageBox.information(self, "成功", "设置已应用，部分设置可能需要重启应用程序才能生效")
    
    def save_and_close(self):
        """保存设置并关闭对话框"""
        self.apply_settings()
        self.accept()
    
    def reset_to_defaults(self):
        """重置为默认设置"""
        reply = QMessageBox.question(
            self, "确认", "确定要重置所有设置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 重置配置
            self.config_manager.reset_to_defaults()
            
            # 重新加载设置
            self.load_settings()
            
            QMessageBox.information(self, "成功", "所有设置已重置为默认值")