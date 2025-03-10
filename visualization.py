import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(PlotCanvas, self).__init__(self.fig)
        self.setParent(parent)

class Visualizer:
    def __init__(self):
        self.canvas = None
        
    def set_canvas(self, canvas):
        """设置画布"""
        self.canvas = canvas
        
    def clear_plot(self):
        """清除图表"""
        if self.canvas:
            self.canvas.axes.clear()
            self.canvas.draw()
    
    def scatter_plot(self, data, x_col, y_col, title=None, x_label=None, y_label=None, color='blue', size=20, alpha=0.7):
        """绘制散点图"""
        if self.canvas is None:
            return False, "画布未初始化"
        
        try:
            x = data[x_col]
            y = data[y_col]
            
            self.canvas.axes.clear()
            self.canvas.axes.scatter(x, y, c=color, s=size, alpha=alpha)
            
            # 设置标题和标签
            if title:
                self.canvas.axes.set_title(title)
            if x_label:
                self.canvas.axes.set_xlabel(x_label)
            else:
                self.canvas.axes.set_xlabel(x_col)
            if y_label:
                self.canvas.axes.set_ylabel(y_label)
            else:
                self.canvas.axes.set_ylabel(y_col)
            
            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            return True, "散点图绘制成功"
        except Exception as e:
            return False, f"散点图绘制失败: {str(e)}"
    
    def scatter_plot_with_error(self, data, x_col, y_col, xerr_col=None, yerr_col=None, 
                               title=None, x_label=None, y_label=None, color='blue', size=20, alpha=0.7):
        """绘制带误差棒的散点图"""
        if self.canvas is None:
            return False, "画布未初始化"
        
        try:
            x = data[x_col]
            y = data[y_col]
            
            xerr = data[xerr_col] if xerr_col else None
            yerr = data[yerr_col] if yerr_col else None
            
            self.canvas.axes.clear()
            self.canvas.axes.errorbar(x, y, xerr=xerr, yerr=yerr, fmt='o', 
                                     ecolor='black', capsize=5, capthick=1, 
                                     color=color, markersize=size, alpha=alpha)
            
            # 设置标题和标签
            if title:
                self.canvas.axes.set_title(title)
            if x_label:
                self.canvas.axes.set_xlabel(x_label)
            else:
                self.canvas.axes.set_xlabel(x_col)
            if y_label:
                self.canvas.axes.set_ylabel(y_label)
            else:
                self.canvas.axes.set_ylabel(y_col)
            
            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            return True, "带误差棒的散点图绘制成功"
        except Exception as e:
            return False, f"带误差棒的散点图绘制失败: {str(e)}"
    
    def histogram(self, data, col, bins=10, title=None, x_label=None, y_label="频率", color='blue', alpha=0.7):
        """绘制直方图"""
        if self.canvas is None:
            return False, "画布未初始化"
        
        try:
            values = data[col]
            
            self.canvas.axes.clear()
            self.canvas.axes.hist(values, bins=bins, color=color, alpha=alpha)
            
            # 设置标题和标签
            if title:
                self.canvas.axes.set_title(title)
            if x_label:
                self.canvas.axes.set_xlabel(x_label)
            else:
                self.canvas.axes.set_xlabel(col)
            self.canvas.axes.set_ylabel(y_label)
            
            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            return True, "直方图绘制成功"
        except Exception as e:
            return False, f"直方图绘制失败: {str(e)}"
    
    def density_map_2d(self, data, x_col, y_col, bins=20, title=None, x_label=None, y_label=None, cmap='viridis'):
        """绘制2D密度图"""
        if self.canvas is None:
            return False, "画布未初始化"
        
        try:
            x = data[x_col]
            y = data[y_col]
            
            self.canvas.axes.clear()
            h, xedges, yedges, im = self.canvas.axes.hist2d(x, y, bins=bins, cmap=cmap)
            
            # 添加颜色条
            cbar = self.canvas.fig.colorbar(im, ax=self.canvas.axes)
            cbar.set_label('密度')
            
            # 设置标题和标签
            if title:
                self.canvas.axes.set_title(title)
            if x_label:
                self.canvas.axes.set_xlabel(x_label)
            else:
                self.canvas.axes.set_xlabel(x_col)
            if y_label:
                self.canvas.axes.set_ylabel(y_label)
            else:
                self.canvas.axes.set_ylabel(y_col)
            
            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            return True, "2D密度图绘制成功"
        except Exception as e:
            return False, f"2D密度图绘制失败: {str(e)}"

    def box_plot(self, data, column, title=None, x_label=None, y_label=None, color='blue'):
        """绘制箱线图"""
        if self.canvas is None:
            return False, "画布未初始化"
        
        try:
            self.canvas.axes.clear()
            self.canvas.axes.boxplot(data[column], vert=True, patch_artist=True,
                                   boxprops=dict(facecolor=color, color='black'),
                                   whiskerprops=dict(color='black'),
                                   capprops=dict(color='black'),
                                   medianprops=dict(color='red'))
            
            # 设置标题和标签
            if title:
                self.canvas.axes.set_title(title)
            if y_label:
                self.canvas.axes.set_ylabel(y_label)
            else:
                self.canvas.axes.set_ylabel(column)
            
            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            return True, "箱线图绘制成功"
        except Exception as e:
            return False, f"箱线图绘制失败: {str(e)}"
    
    def line_plot(self, data, x_col, y_col, title=None, x_label=None, y_label=None, 
                 color='blue', marker='o', linestyle='-', linewidth=2):
        """绘制折线图"""
        if self.canvas is None:
            return False, "画布未初始化"
        
        try:
            x = data[x_col]
            y = data[y_col]
            
            self.canvas.axes.clear()
            self.canvas.axes.plot(x, y, marker=marker, linestyle=linestyle, 
                                linewidth=linewidth, color=color)
            
            # 设置标题和标签
            if title:
                self.canvas.axes.set_title(title)
            if x_label:
                self.canvas.axes.set_xlabel(x_label)
            else:
                self.canvas.axes.set_xlabel(x_col)
            if y_label:
                self.canvas.axes.set_ylabel(y_label)
            else:
                self.canvas.axes.set_ylabel(y_col)
            
            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            return True, "折线图绘制成功"
        except Exception as e:
            return False, f"折线图绘制失败: {str(e)}"