from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTabWidget, QTextBrowser, QWidget)
from PyQt6.QtCore import Qt
import pandas as pd
import numpy as np

class HelpDialog(QDialog):
    """帮助对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("PlotData 帮助")
        self.setMinimumSize(700, 500)
        
        self.init_ui()
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 基本使用选项卡
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        basic_help = QTextBrowser()
        basic_help.setOpenExternalLinks(True)
        basic_help.setHtml(self.get_basic_help_text())
        
        basic_layout.addWidget(basic_help)
        
        tab_widget.addTab(basic_tab, "基本使用")
        
        # 数据处理选项卡
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        data_help = QTextBrowser()
        data_help.setOpenExternalLinks(True)
        data_help.setHtml(self.get_data_help_text())
        
        data_layout.addWidget(data_help)
        
        tab_widget.addTab(data_tab, "数据处理")
        
        # 图表选项卡
        plot_tab = QWidget()
        plot_layout = QVBoxLayout(plot_tab)
        
        plot_help = QTextBrowser()
        plot_help.setOpenExternalLinks(True)
        plot_help.setHtml(self.get_plot_help_text())
        
        plot_layout.addWidget(plot_help)
        
        tab_widget.addTab(plot_tab, "图表绘制")
        
        # 快捷键选项卡
        shortcut_tab = QWidget()
        shortcut_layout = QVBoxLayout(shortcut_tab)
        
        shortcut_help = QTextBrowser()
        shortcut_help.setOpenExternalLinks(True)
        shortcut_help.setHtml(self.get_shortcut_help_text())
        
        shortcut_layout.addWidget(shortcut_help)
        
        tab_widget.addTab(shortcut_tab, "快捷键")
        
        main_layout.addWidget(tab_widget)
        
        # 创建按钮
        buttons_layout = QHBoxLayout()
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        main_layout.addLayout(buttons_layout)
    
    def get_basic_help_text(self):
        """获取基本使用帮助文本"""
        return """
        <h2>PlotData 基本使用指南</h2>
        
        <h3>1. 打开数据文件</h3>
        <p>点击菜单栏中的 <b>文件 > 打开</b> 或使用快捷键 <b>Ctrl+O</b> 打开数据文件。</p>
        <p>支持的文件格式包括:</p>
        <ul>
            <li>CSV 文件 (*.csv)</li>
            <li>Excel 文件 (*.xlsx, *.xls)</li>
            <li>JSON 文件 (*.json)</li>
        </ul>
        
        <h3>2. 查看数据</h3>
        <p>数据加载后，将在左侧面板中显示表格视图。您可以:</p>
        <ul>
            <li>滚动浏览数据</li>
            <li>点击列标题排序数据</li>
            <li>调整列宽</li>
        </ul>
        
        <h3>3. 导出数据</h3>
        <p>点击 <b>文件 > 导出数据</b> 或使用快捷键 <b>Ctrl+E</b> 将当前数据导出为不同格式。</p>
        
        <h3>4. 切换主题</h3>
        <p>点击 <b>视图 > 切换深色/浅色主题</b> 或使用快捷键 <b>Ctrl+T</b> 在深色和浅色主题之间切换。</p>
        """
    
    def get_data_help_text(self):
        """获取数据处理帮助文本"""
        return """
        <h2>数据处理功能</h2>
        
        <h3>1. 数据清洗</h3>
        <p>点击 <b>数据 > 数据清洗</b> 打开数据清洗对话框，您可以:</p>
        <ul>
            <li>处理缺失值 (删除或填充)</li>
            <li>删除重复行</li>
            <li>筛选数据</li>
            <li>转换数据类型</li>
        </ul>
        
        <h3>2. 数据筛选</h3>
        <p>在数据视图中，您可以使用筛选功能来显示符合特定条件的数据行。</p>
        
        <h3>3. 数据统计</h3>
        <p>查看数据的基本统计信息，包括:</p>
        <ul>
            <li>均值、中位数、标准差</li>
            <li>最大值、最小值</li>
            <li>数据分布</li>
        </ul>
        
        <h3>4. 数据转换</h3>
        <p>对数据进行各种转换操作:</p>
        <ul>
            <li>标准化/归一化</li>
            <li>对数转换</li>
            <li>分类变量编码</li>
        </ul>
        """
    
    def get_plot_help_text(self):
        """获取图表绘制帮助文本"""
        return """
        <h2>图表绘制指南</h2>
        
        <h3>1. 创建图表</h3>
        <p>在右侧面板中，您可以选择不同类型的图表:</p>
        <ul>
            <li><b>散点图</b>: 显示两个变量之间的关系</li>
            <li><b>折线图</b>: 显示数据随时间或顺序的变化趋势</li>
            <li><b>柱状图</b>: 比较不同类别的数据</li>
            <li><b>饼图</b>: 显示部分与整体的关系</li>
            <li><b>直方图</b>: 显示数据的分布情况</li>
            <li><b>箱线图</b>: 显示数据的分布和异常值</li>
        </ul>
        
        <h3>2. 自定义图表</h3>
        <p>您可以自定义图表的各种属性:</p>
        <ul>
            <li>标题和轴标签</li>
            <li>颜色和样式</li>
            <li>图例位置</li>
            <li>网格线</li>
            <li>字体大小</li>
        </ul>
        
        <h3>3. 导出图表</h3>
        <p>创建图表后，您可以将其导出为多种格式:</p>
        <ul>
            <li>PNG 图像</li>
            <li>JPG 图像</li>
            <li>PDF 文档</li>
            <li>SVG 矢量图</li>
        </ul>
        """
    
    def get_shortcut_help_text(self):
        """获取快捷键帮助文本"""
        return """
        <h2>快捷键列表</h2>
        
        <table border="1" cellspacing="0" cellpadding="5">
            <tr>
                <th>快捷键</th>
                <th>功能</th>
            </tr>
            <tr>
                <td>Ctrl+O</td>
                <td>打开数据文件</td>
            </tr>
            <tr>
                <td>Ctrl+E</td>
                <td>导出数据</td>
            </tr>
            <tr>
                <td>Ctrl+P</td>
                <td>打开首选项</td>
            </tr>
            <tr>
                <td>Ctrl+T</td>
                <td>切换深色/浅色主题</td>
            </tr>
            <tr>
                <td>Ctrl+Q</td>
                <td>退出应用程序</td>
            </tr>
            <tr>
                <td>F1</td>
                <td>打开帮助</td>
            </tr>
        </table>
        """