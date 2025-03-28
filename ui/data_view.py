import pandas as pd
import numpy as np
from PyQt6 import sip
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableView, QHeaderView, QComboBox, 
                            QGroupBox, QMessageBox, QTextEdit,QApplication,
                            QDialog, QListWidget, QListWidgetItem)
from PyQt6.QtCore import (Qt, QAbstractTableModel, QModelIndex, pyqtSignal,
                          QMetaObject, Qt, QThread, pyqtSignal)

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
    
    plot_requested = pyqtSignal(str, str, str, str, str, str, str, int, str, int, str)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()  # 确保初始化方法被调用
       
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建工具栏
        toolbar_layout = QHBoxLayout()
        
        # 添加载入数据按钮到工具栏
        self.load_data_button = QPushButton("载入数据")
        self.load_data_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogOpenButton))
        self.load_data_button.clicked.connect(self.load_data)
        toolbar_layout.addWidget(self.load_data_button)
        

        
        # 添加导出数据按钮到工具栏
        self.export_data_button = QPushButton("导出数据")
        self.export_data_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton))
        self.export_data_button.clicked.connect(self.export_data)
        toolbar_layout.addWidget(self.export_data_button)

        # 在工具栏中添加清除数据按钮
        self.clear_button = QPushButton("清除数据")
        self.clear_button.setToolTip("清除当前数据以便加载新数据")
        self.clear_button.clicked.connect(self.clear_data)
        toolbar_layout.addWidget(self.clear_button)

        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)
        
        # 创建数据表视图
        self.table_label = QLabel("")
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
        
        # 添加数据筛选区域 - 移到绘图控制前面
        filter_group = QGroupBox("数据筛选")
        filter_group.setStyleSheet("QGroupBox { max-height: 120px; }")
        filter_layout = QVBoxLayout(filter_group)
        filter_layout.setContentsMargins(5, 5, 5, 5)  # 减小内边距
        filter_layout.setSpacing(3)  # 减小控件间距
        
        # 添加筛选表达式区域 - 使用更紧凑的布局
        filter_expr_layout = QHBoxLayout()
        self.filter_expr_edit = QTextEdit()
        self.filter_expr_edit.setPlaceholderText("示例: `列名` > 10 & `列名` < 100")
        filter_expr_layout.addWidget(self.filter_expr_edit)
        filter_layout.addLayout(filter_expr_layout)
        
        # 创建按钮布局 - 使用更紧凑的布局
        filter_btn_layout = QHBoxLayout()
        filter_btn_layout.setSpacing(5)  # 减小按钮间距
        
        # 显示可用列名按钮
        self.show_columns_btn = QPushButton("显示可用列名")
        self.show_columns_btn.clicked.connect(self.show_available_columns)
        self.show_columns_btn.setMaximumHeight(25)  # 减小按钮高度
        filter_btn_layout.addWidget(self.show_columns_btn)
        
        # 应用筛选按钮
        self.apply_filter_btn = QPushButton("应用筛选")
        self.apply_filter_btn.clicked.connect(self.apply_filter)
        self.apply_filter_btn.setMaximumHeight(25)  # 减小按钮高度
        filter_btn_layout.addWidget(self.apply_filter_btn)
        
        # 清除筛选按钮
        self.clear_filter_btn = QPushButton("清除筛选")
        self.clear_filter_btn.clicked.connect(self.clear_filter)
        self.clear_filter_btn.setMaximumHeight(25)  # 减小按钮高度
        filter_btn_layout.addWidget(self.clear_filter_btn)
        
        filter_layout.addLayout(filter_btn_layout)
        
        # 添加筛选区域到主布局
        main_layout.addWidget(filter_group)
        
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
                print("警告：数据为空")
                return
    
            # 新增：清理列名中的空格
            data.columns = data.columns.str.replace(' ', '')  # 移除列名中的空格
    
            # 统一更新表格模型
            self.table_model.update_data(data)
            
            columns = list(data.columns)
            
            # 安全更新所有下拉框
            self.safe_update_comboboxes(columns)
            
            # 更新标签显示
            self.table_label.setText(f"数据预览: {len(data)}行 x {len(data.columns)}列")
    
            # 打印调试信息
            print(f"已更新数据视图，列数：{len(columns)}，行数：{len(data)}")
    
            # 通知 PlotView 更新
            main_window = self.window()
            if hasattr(main_window, 'plot_view') and main_window.plot_view:
                try:
                    main_window.plot_view.update_columns()
                    print("已通知 PlotView 更新列选择下拉框")
                except Exception as e:
                    print(f"通知 PlotView 更新时出错: {str(e)}")
                    import traceback
                    traceback.print_exc()
    
        except Exception as e:
            print(f"更新数据视图时出错: {str(e)}")
            import traceback
            traceback.print_exc()

    def safe_update_comboboxes(self, columns):
        """安全更新所有下拉框"""
        try:
            # 检查列名是否为空
            if not columns or len(columns) == 0:
                print("警告：没有可用的列名")
                return
                
            print(f"正在更新下拉框，可用列：{columns}")

            # 只更新 DataView 中实际存在的下拉框
            # 例如，如果有 filter_col_combo 这样的属性，可以保留
            if hasattr(self, 'filter_col_combo') and not sip.isdeleted(self.filter_col_combo):
                current_text = self.filter_col_combo.currentText() if self.filter_col_combo.count() > 0 else ""
                self.filter_col_combo.blockSignals(True)
                self.filter_col_combo.clear()
                self.filter_col_combo.addItems(columns)
                if current_text in columns:
                    self.filter_col_combo.setCurrentText(current_text)
                self.filter_col_combo.blockSignals(False)
            
            # 通知 PlotView 更新其下拉框
            main_window = self.window()
            if hasattr(main_window, 'plot_view') and main_window.plot_view:
                # 调用 PlotView 的更新方法
                main_window.plot_view.update_columns()
                print("已通知 PlotView 更新列选择下拉框")
            else:
                print("无法找到 PlotView 对象，无法更新列选择下拉框")
                
            print("下拉框更新完成")
                
        except Exception as e:
            print(f"更新下拉框时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def request_plot(self):
        """请求绘图 - 将请求转发到 PlotView"""
        try:
            # 获取主窗口
            main_window = self.window()
            if hasattr(main_window, 'plot_view') and main_window.plot_view:
                # 调用 PlotView 的绘图方法
                print("正在请求绘图...")
                # 防止重复调用
                if hasattr(main_window.plot_view, '_is_plotting') and main_window.plot_view._is_plotting:
                    print("绘图正在进行中，请稍候...")
                    return
                    
                main_window.plot_view.request_plot()
                print("已将绘图请求转发到 PlotView")
            else:
                print("无法找到 PlotView 对象")
                QMessageBox.warning(self, "错误", "无法找到绘图视图组件")
                return
        except Exception as e:
            print(f"绘图请求转发失败: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"绘图请求转发失败: {str(e)}")
            return

    def apply_filter(self):
        """应用新的多条件筛选"""
        expr = self.filter_expr_edit.toPlainText().strip()
        
        try:
            if expr:
                # 转换逻辑运算符为Pandas兼容格式
                expr = expr.replace(' and ', ' & ').replace(' or ', ' | ')
                
                # 获取原始数据
                raw_data = self.data_manager.get_data(filtered=False)
                
                # 执行筛选
                success, message = self.data_manager.set_filtered_data(expr, raw_data)
                
                if success:
                    # 使用数据管理器的显示数据接口
                    display_data = self.data_manager.get_display_data()
                    self.table_model.update_data(display_data)
                    # 添加筛选状态标记
                    self.filter_applied = True
                    info_msg = f"筛选结果: {len(display_data)} 行 (原始数据 {len(raw_data)} 行)"
                    self.table_label.setText(info_msg)
                else:
                    QMessageBox.warning(self, "筛选错误", message)
            else:
                self.clear_filter()
                
        except Exception as e:
            error_detail = str(e)
            # 添加列名提示
            if "未定义的列名" in error_detail or "列名不存在" in error_detail:
                error_detail += "\n\n列名使用建议：\n"
                error_detail += "1. 包含空格或特殊字符时使用反引号包裹，如：`Column Name`\n"
                error_detail += "2. 检查列名拼写（区分大小写）\n"
                error_detail += "3. 使用下方列选择器获取有效列名"
                
            QMessageBox.critical(self, "筛选错误", 
                               f"表达式错误: {error_detail}\n\n表达式示例：\n"
                               "数值范围: `MJD` > 52000 & `MJD` < 60000\n"
                               "多条件组合: (`Column A` > 5) | (`Column B` < 3)")

            self.clear_filter()

    def clear_filter(self):
        """清除筛选条件"""
        # 恢复原始数据
        data = self.data_manager.get_data()
        self.table_model.update_data(data)

        # 清空筛选后的数据
        self.data_manager.clear_filtered_data()

        # 清空筛选输入
        self.filter_expr_edit.clear()
        
        # 更新状态信息
        self.table_label.setText("数据预览")
    
    # 添加重置筛选功能
    def reset_filter(self):
        """重置数据筛选"""
        self.data_manager.reset_filter()
        # 更新表格显示原始数据
        self.table_model.update_data(self.data_manager.get_data(filtered=False))
        QMessageBox.information(self, "提示", "已重置筛选，显示所有数据")

    # 添加显示可用列名的方法
    def show_available_columns(self):
        """显示当前数据中可用的列名"""
        if not self.data_manager or self.data_manager.get_data() is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
            
        columns = self.data_manager.get_column_names()
        if not columns:
            QMessageBox.information(self, "列名", "当前数据没有可用列")
            return
            
        # 创建列名对话框
        columns_dialog = QDialog(self)
        columns_dialog.setWindowTitle("可用列名")
        columns_dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(columns_dialog)
        
        # 添加说明文本
        info_label = QLabel("以下是当前数据中的可用列名，双击可复制到筛选表达式:")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 创建列表显示所有列名
        columns_list = QListWidget()
        for col in columns:
            item = QListWidgetItem(f"`{col}`")
            item.setData(Qt.ItemDataRole.UserRole, col)
            columns_list.addItem(item)
        
        # 双击列名时复制到筛选表达式
        columns_list.itemDoubleClicked.connect(
            lambda item: self.insert_column_to_filter(item.data(Qt.ItemDataRole.UserRole))
        )
        
        layout.addWidget(columns_list)
        
        # 添加关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(columns_dialog.accept)
        layout.addWidget(close_btn)
        
        columns_dialog.exec()
    
    def insert_column_to_filter(self, column_name):
        """将列名插入到筛选表达式中"""
        current_text = self.filter_expr_edit.toPlainText()
        cursor = self.filter_expr_edit.textCursor()
        cursor.insertText(f"`{column_name}`")
        self.filter_expr_edit.setFocus()

    # 在数据加载后调用此方法
    def on_data_loaded(self):
        """数据加载后的处理"""
        try:
            # 检查数据是否有效
            if self.data_manager.get_data() is None:
                raise ValueError("加载的数据为空")            

            # 更新数据视图
            self.update_data_view()

            # 启用筛选控制
            filter_group = self.findChild(QGroupBox, "数据筛选")
            if filter_group:
                filter_group.setEnabled(True)
            
            # 启用UI
            self.setEnabled(True)

        except Exception as e:
            print(f"数据加载后处理出错: {str(e)}")
            self.setEnabled(True)

    def load_data(self):
        """载入数据按钮点击事件处理"""
        try:
            parent = self.window()
            if hasattr(parent, 'open_file'):
                # 新增：先禁用UI防止重复操作
                self.setEnabled(False)  
                QApplication.processEvents()

                # 先断开之前的连接，避免重复连接
                try:
                    self.data_manager.data_loaded.disconnect()
                except TypeError:
                    pass
                # 连接信号
                self.data_manager.data_loaded.connect(
                    self.on_data_loaded, 
                    Qt.ConnectionType.QueuedConnection
                )
            
                # 调用主窗口的打开文件方法
                success = parent.open_file()
                if not success:
                    self.setEnabled(True)
                    return False, "文件打开失败"
                
                return True, "数据加载成功"
            else:
                return False, "无法找到主窗口"
        except Exception as e:
            self.setEnabled(True)
            return False, f"数据加载出错: {str(e)}"

    def export_data(self):
        """导出数据按钮点击事件处理"""
        # 同样，这里需要调用主窗口的导出文件方法
        parent = self.window()
        if hasattr(parent, 'export_data'):
            parent.export_data()

    def on_color_changed(self, color):
        """颜色选择回调"""
        self.color_button.setStyleSheet(f"background-color: {color.name()};")
        self.color_button.setProperty("color", color.name())  # 新增属性存储

    def create_buttons(self):
        button_layout = QHBoxLayout()
        
        # 载入数据按钮
        self.load_button = QPushButton("载入数据")
        button_layout.addWidget(self.load_button)

        # 新增预览按钮
        self.preview_toggle_button = QPushButton("数据预览 ✓")
        self.preview_toggle_button.setCheckable(True)
        self.preview_toggle_button.setChecked(True)
        self.preview_toggle_button.clicked.connect(self.toggle_preview)
        button_layout.addWidget(self.preview_toggle_button)

        # 导出数据按钮
        self.export_button = QPushButton("导出数据") 
        button_layout.addWidget(self.export_button)

        return button_layout

    def clear_data(self):
        """清除当前数据"""
        # 确认操作
        reply = QMessageBox.question(
            self, 
            "确认清除", 
            "确定要清除当前数据吗？这将重置所有设置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 清除数据管理器中的数据
            self.data_manager.data = None
            self.data_manager.filtered_data = None
            self.data_manager.current_file = None
            
            # 更新数据视图
            self.update_data_view()
            
            # 清除筛选条件
            self.clear_filter()
            
            # 通知主窗口更新状态
            parent = self.window()
            if hasattr(parent, 'update_status'):
                parent.update_status("数据已清除")