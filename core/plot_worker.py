import logging
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable, QThreadPool
import pandas as pd
import traceback

class PlotWorkerSignals(QObject):
    """工作线程信号类，用于在线程间通信"""
    # 定义信号
    finished = pyqtSignal(bool, str)  # 完成信号，返回成功状态和消息
    progress = pyqtSignal(int)        # 进度信号
    error = pyqtSignal(str)           # 错误信号

class PlotWorker(QRunnable):
    """绘图工作线程类，用于处理耗时的绘图操作"""
    
    def __init__(self, visualizer, plot_type, data, **kwargs):
        super().__init__()
        
        # 设置线程优先级
        self.setAutoDelete(True)
        
        # 保存参数
        self.visualizer = visualizer
        self.plot_type = plot_type
        self.data = data.copy()  # 创建数据副本，避免修改原始数据
        self.kwargs = kwargs
        
        # 创建信号对象
        self.signals = PlotWorkerSignals()
        
        # 获取日志记录器
        self.logger = logging.getLogger("PlotData.PlotWorker")
        self.logger.info(f"创建绘图工作线程: {plot_type}")
    
    @pyqtSlot()
    def run(self):
        """线程执行函数"""
        try:
            self.logger.info(f"开始执行绘图任务: {self.plot_type}")
            
            # 预处理数据，确保数据类型正确
            self._preprocess_data()
            
            # 根据绘图类型调用不同的绘图方法
            result = False
            message = ""
            
            if self.plot_type == "散点图":
                result, message = self._draw_scatter()
            elif self.plot_type == "带误差棒的散点图":
                result, message = self._draw_scatter_with_error()
            elif self.plot_type == "直方图":
                result, message = self._draw_histogram()
            elif self.plot_type == "2D密度图":
                result, message = self._draw_density_map_2d()
            else:
                message = f"不支持的绘图类型: {self.plot_type}"
                self.logger.error(message)
            
            # 发送完成信号
            self.signals.finished.emit(result, message)
            
        except Exception as e:
            # 记录错误并发送错误信号
            error_msg = f"绘图过程中发生错误: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            self.signals.error.emit(error_msg)
            self.signals.finished.emit(False, error_msg)
    
    def _preprocess_data(self):
        """预处理数据，确保数据类型正确"""
        # 获取列名
        x_col = self.kwargs.get('x_col')
        y_col = self.kwargs.get('y_col')
        xerr_col = self.kwargs.get('xerr_col')
        yerr_col = self.kwargs.get('yerr_col')
        
        # 确保X和Y列是数值类型
        if x_col and x_col in self.data.columns:
            self.data[x_col] = pd.to_numeric(self.data[x_col], errors='coerce')
        
        if y_col and y_col in self.data.columns:
            self.data[y_col] = pd.to_numeric(self.data[y_col], errors='coerce')
        
        # 处理误差列
        if xerr_col and xerr_col in self.data.columns:
            self.data[xerr_col] = pd.to_numeric(self.data[xerr_col], errors='coerce')
        
        if yerr_col and yerr_col in self.data.columns:
            self.data[yerr_col] = pd.to_numeric(self.data[yerr_col], errors='coerce')
    
    def _draw_scatter(self):
        """绘制散点图"""
        x_col = self.kwargs.get('x_col')
        y_col = self.kwargs.get('y_col')
        color = self.kwargs.get('color', 'blue')
        mark_style = self.kwargs.get('mark_style', 'o')
        mark_size = self.kwargs.get('mark_size', 10)
        alpha = self.kwargs.get('alpha', 0.7)
        title = self.kwargs.get('title')
        x_label = self.kwargs.get('x_label')
        y_label = self.kwargs.get('y_label')
        x_min = self.kwargs.get('x_min')
        x_max = self.kwargs.get('x_max')
        y_min = self.kwargs.get('y_min')
        y_max = self.kwargs.get('y_max')
        x_major_ticks = self.kwargs.get('x_major_ticks', 5)
        x_minor_ticks = self.kwargs.get('x_minor_ticks', 1)
        x_show_grid = self.kwargs.get('x_show_grid', True)
        y_major_ticks = self.kwargs.get('y_major_ticks', 5)
        y_minor_ticks = self.kwargs.get('y_minor_ticks', 1)
        y_show_grid = self.kwargs.get('y_show_grid', True)
        
        return self.visualizer.scatter_plot(
            self.data, x_col, y_col, 
            title=title, 
            x_label=x_label, 
            y_label=y_label, 
            color=color, 
            alpha=alpha, 
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
    
    def _draw_scatter_with_error(self):
        """绘制带误差棒的散点图"""
        x_col = self.kwargs.get('x_col')
        y_col = self.kwargs.get('y_col')
        xerr_col = self.kwargs.get('xerr_col')
        yerr_col = self.kwargs.get('yerr_col')
        color = self.kwargs.get('color', 'blue')
        mark_style = self.kwargs.get('mark_style', 'o')
        mark_size = self.kwargs.get('mark_size', 10)
        alpha = self.kwargs.get('alpha', 0.7)
        title = self.kwargs.get('title')
        x_label = self.kwargs.get('x_label')
        y_label = self.kwargs.get('y_label')
        x_min = self.kwargs.get('x_min')
        x_max = self.kwargs.get('x_max')
        y_min = self.kwargs.get('y_min')
        y_max = self.kwargs.get('y_max')
        x_major_ticks = self.kwargs.get('x_major_ticks', 5)
        x_minor_ticks = self.kwargs.get('x_minor_ticks', 1)
        x_show_grid = self.kwargs.get('x_show_grid', True)
        y_major_ticks = self.kwargs.get('y_major_ticks', 5)
        y_minor_ticks = self.kwargs.get('y_minor_ticks', 1)
        y_show_grid = self.kwargs.get('y_show_grid', True)
        
        return self.visualizer.scatter_plot_with_error(
            self.data, x_col, y_col, 
            xerr_col=xerr_col, 
            yerr_col=yerr_col, 
            title=title, 
            x_label=x_label, 
            y_label=y_label, 
            color=color, 
            alpha=alpha, 
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
    
    def _draw_histogram(self):
        """绘制直方图"""
        x_col = self.kwargs.get('x_col')
        bins = self.kwargs.get('bins', 50)
        histtype = self.kwargs.get('histtype', 'bar')
        color = self.kwargs.get('color', 'blue')
        alpha = self.kwargs.get('alpha', 0.7)
        title = self.kwargs.get('title')
        x_label = self.kwargs.get('x_label')
        y_label = self.kwargs.get('y_label', '频率')
        x_min = self.kwargs.get('x_min')
        x_max = self.kwargs.get('x_max')
        y_min = self.kwargs.get('y_min')
        y_max = self.kwargs.get('y_max')
        x_major_ticks = self.kwargs.get('x_major_ticks', 5)
        x_minor_ticks = self.kwargs.get('x_minor_ticks', 1)
        x_show_grid = self.kwargs.get('x_show_grid', True)
        y_major_ticks = self.kwargs.get('y_major_ticks', 5)
        y_minor_ticks = self.kwargs.get('y_minor_ticks', 1)
        y_show_grid = self.kwargs.get('y_show_grid', True)
        
        return self.visualizer.histogram(
            self.data, x_col, 
            bins=bins, 
            title=title, 
            x_label=x_label, 
            y_label=y_label, 
            color=color, 
            histtype=histtype, 
            alpha=alpha,
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
    
    def _draw_density_map_2d(self):
        """绘制2D密度图"""
        x_col = self.kwargs.get('x_col')
        y_col = self.kwargs.get('y_col')
        bins = self.kwargs.get('bins', 50)
        colormap = self.kwargs.get('colormap', 'viridis')
        title = self.kwargs.get('title')
        x_label = self.kwargs.get('x_label')
        y_label = self.kwargs.get('y_label')
        x_min = self.kwargs.get('x_min')
        x_max = self.kwargs.get('x_max')
        y_min = self.kwargs.get('y_min')
        y_max = self.kwargs.get('y_max')
        x_major_ticks = self.kwargs.get('x_major_ticks', 5)
        x_minor_ticks = self.kwargs.get('x_minor_ticks', 1)
        x_show_grid = self.kwargs.get('x_show_grid', True)
        y_major_ticks = self.kwargs.get('y_major_ticks', 5)
        y_minor_ticks = self.kwargs.get('y_minor_ticks', 1)
        y_show_grid = self.kwargs.get('y_show_grid', True)
        
        return self.visualizer.density_map_2d(
            self.data, x_col, y_col, 
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