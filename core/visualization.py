import numpy as np
import traceback
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize, ListedColormap
import matplotlib.ticker as ticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']  # First try Microsoft YaHei, then SimHei
matplotlib.rcParams['axes.unicode_minus'] = False  # Fix minus sign display issue

class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(PlotCanvas, self).__init__(self.fig)
        self.setParent(parent)

        # 确保子图规范有效
        if not hasattr(self.axes, 'get_subplotspec'):
            self.axes = self.fig.add_subplot(111)
        self.fig.tight_layout()

class Visualizer:
    def __init__(self):
        self.canvas = None
        self.colorbar = None
        self.current_colorbar = None
        
    def set_canvas(self, canvas):
        """设置画布"""
        self.canvas = canvas
        
    def clear_plot(self):
        """清除图表"""
        if self.canvas:
            # 完全重置图形 - 最彻底的方式
            self.canvas.fig.clear()
            
            # 重新创建主axes
            self.canvas.axes = self.canvas.fig.add_subplot(111)
            
            # 确保colorbar引用被清除
            self.colorbar = None
            
            # 重置布局参数
            self.canvas.fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
            self.canvas.draw()
    
    def scatter_plot(self, data, 
        x_col,
        y_col,
        title=None,
        x_label=None,
        y_label=None,
        color='blue',
        alpha=0.7,
        mark_style='o',
        mark_size=10,
        x_major_ticks=5,
        x_minor_ticks=1,
        x_show_grid=True,
        y_major_ticks=5,
        y_minor_ticks=1,
        y_show_grid=True,
        x_min=None,
        x_max=None,
        y_min=None,
        y_max=None):

        """绘制散点图"""
        if self.canvas is None:
            return False, "画布未初始化"

        # 先清除之前的图表
        self.clear_plot()

         # 添加标记样式映射
        style_map = {
            "圆形": 'o',
            "点": '.',
            "方形": 's',
            "三角形": '^',
            "星形": '*',
            "菱形": 'D',
            "十字": 'x',
            "加号": '+',
            "叉号": 'x'
        }
        
        try:
            x = data[x_col]
            y = data[y_col]
            
            self.canvas.axes.clear()
            self.canvas.axes.scatter(x, y,
                marker=mark_style,
                c=color,
                s=mark_size,
                alpha=alpha)
            
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

            # 设置坐标轴范围
            if x_min is not None and x_max is not None and x_min != x_max:
                self.canvas.axes.set_xlim(x_min, x_max)
            if y_min is not None and y_max is not None and y_min != y_max:
                self.canvas.axes.set_ylim(y_min, y_max)

            self._configure_axes(self.canvas.axes, 
                            x_major_ticks, 
                            x_minor_ticks,
                            x_show_grid,
                            y_major_ticks,
                            y_minor_ticks,
                            y_show_grid)

            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            return True, "散点图绘制成功"
        except Exception as e:
            return False, f"散点图绘制失败: {str(e)}"
    
    def scatter_plot_with_error(self, data, 
        x_col, 
        y_col, 
        xerr_col=None, 
        yerr_col=None,
        title=None,
        x_label=None,
        y_label=None,
        color='blue',
        alpha=0.7, 
        mark_size=10,
        mark_style='o',
        x_major_ticks=5,  # 修改为X轴主刻度
        x_minor_ticks=1,  # 修改为X轴次刻度
        x_show_grid=True, # 修改为X轴网格线
        y_major_ticks=5,  # 添加Y轴主刻度
        y_minor_ticks=1,  # 添加Y轴次刻度
        y_show_grid=True, # 添加Y轴网格线
        x_min=None, 
        x_max=None, 
        y_min=None, 
        y_max=None):

        """绘制带误差棒的散点图"""
        if self.canvas is None:
            return False, "画布未初始化"

        # 先清除之前的图表
        self.clear_plot()

        # 添加标记样式映射
        style_map = {
            "圆形": 'o',
            "点": '.',
            "方形": 's',
            "三角形": '^',
            "星形": '*',
            "菱形": 'D',
            "十字": 'x',
            "加号": '+',
            "叉号": 'x'
        }
        
        try:
            x = data[x_col]
            y = data[y_col]
            
            xerr = data[xerr_col] if xerr_col and xerr_col != "无" else None
            yerr = data[yerr_col] if yerr_col and yerr_col != "无" else None
            
            self.canvas.axes.clear()
            # 修改为正确的errorbar参数设置
            self.canvas.axes.errorbar(x, y,
                                    xerr=xerr,
                                    yerr=yerr,
                                    fmt=mark_style,        
                                    linestyle='',       # 改为空字符串确保完全禁用线条
                                    markersize=mark_size,
                                    color=color,
                                    alpha=alpha,
                                    ecolor=color,    # 误差棒颜色
                                    elinewidth=1.5,   # 误差棒线宽
                                    capsize=5)        # 误差棒端帽长度
            
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

            # 设置坐标轴范围
            if x_min is not None and x_max is not None and x_min != x_max:
                self.canvas.axes.set_xlim(x_min, x_max)
            if y_min is not None and y_max is not None and y_min != y_max:
                self.canvas.axes.set_ylim(y_min, y_max)

            self._configure_axes(self.canvas.axes, 
                x_major_ticks,  # 修改参数
                x_minor_ticks,  # 修改参数
                x_show_grid,    # 修改参数
                y_major_ticks,  # 添加参数
                y_minor_ticks,  # 添加参数
                y_show_grid)    # 添加参数
            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            return True, "带误差棒的散点图绘制成功"
        except Exception as e:
            return False, f"带误差棒的散点图绘制失败: {str(e)}"
    
    def histogram(self, data, col, 
        bins=10,
        title=None,
        x_label=None,
        y_label="次数",
        color='blue',
        histtype='bar',
        alpha=0.7,
        edgecolor='black',
        hatch='/',
        x_major_ticks=5,  # 修改为X轴主刻度
        x_minor_ticks=1,  # 修改为X轴次刻度
        x_show_grid=True, # 修改为X轴网格线
        y_major_ticks=5,  # 添加Y轴主刻度
        y_minor_ticks=1,  # 添加Y轴次刻度
        y_show_grid=True, # 添加Y轴网格线
        x_min=None, 
        x_max=None, 
        y_min=None, 
        y_max=None,
        **kwargs):
        """绘制直方图
        Args:
            data: pandas DataFrame
            x_col: str, x轴数据列名
            bins: int, 分箱数量
            color: str, 颜色
            histtype: str, 直方图类型 ('bar', 'barstacked', 'step', 'stepfilled')
            alpha: float, 透明度
            **kwargs: 其他参数
        """
        if self.canvas is None:
            return False, "画布未初始化"

        # 先清除之前的图表
        self.clear_plot()
        
        try:
            values = data[col]
            
            self.canvas.axes.clear()
            self.canvas.axes.hist(values, 
                bins=bins,
                color=color,
                histtype = histtype,
                edgecolor = 'black',
                hatch = '/',
                alpha=alpha)
            
            # 设置标题和标签
            if title:
                self.canvas.axes.set_title(title)
            if x_label:
                self.canvas.axes.set_xlabel(x_label)
            else:
                self.canvas.axes.set_xlabel(col)
            self.canvas.axes.set_ylabel(y_label)
            
            # 设置坐标轴范围
            if x_min is not None and x_max is not None and x_min != x_max:
                self.canvas.axes.set_xlim(x_min, x_max)
            if y_min is not None and y_max is not None and y_min != y_max:
                self.canvas.axes.set_ylim(y_min, y_max)

            self._configure_axes(self.canvas.axes, 
                x_major_ticks,  # 修改参数
                x_minor_ticks,  # 修改参数
                x_show_grid,    # 修改参数
                y_major_ticks,  # 添加参数
                y_minor_ticks,  # 添加参数
                y_show_grid)    # 添加参数
            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            return True, "直方图绘制成功"
        except Exception as e:
            return False, f"直方图绘制失败: {str(e)}"
    
    def density_map_2d(self, data, x_col, y_col, 
        bins=10, 
        title=None, 
        x_label=None, 
        y_label=None, 
        colormap='viridis',
        colorbar_scale='线性',
        x_major_ticks=5,  # 修改为X轴主刻度
        x_minor_ticks=1,  # 修改为X轴次刻度
        x_show_grid=True, # 修改为X轴网格线
        y_major_ticks=5,  # 添加Y轴主刻度
        y_minor_ticks=1,  # 添加Y轴次刻度
        y_show_grid=True, # 添加Y轴网格线
        x_min=None, 
        x_max=None, 
        y_min=None, 
        y_max=None):

        if self.canvas is None:
            return False, "画布未初始化"

        # 先清除之前的图表
        self.clear_plot()
 
        try:
            # 使用标准清理方法代替直接操作fig
            self.clear_plot()  # 替换原有的fig.clear()

            # 检查列是否存在
            if x_col not in data.columns:
                return False, f"列 '{x_col}' 不存在"
            if y_col not in data.columns:
                return False, f"列 '{y_col}' 不存在"

            # 重置图形布局参数 - 为colorbar预留空间
            self.canvas.fig.subplots_adjust(left=0.15, right=0.95, bottom=0.1, top=0.9)
    
            # 提取数据
            x_data = data[x_col].dropna()
            y_data = data[y_col].dropna()
            
            if len(x_data) == 0 or len(y_data) == 0:
                return False, "没有足够的有效数据点"
            
            # 确保数据长度一致
            min_len = min(len(x_data), len(y_data))
            x_data = x_data[:min_len]
            y_data = y_data[:min_len]
            
            # 计算2D直方图数据
            h, xedges, yedges = np.histogram2d(x_data, y_data, bins=bins)
            
            # 创建网格
            X, Y = np.meshgrid(xedges[:-1] + 0.5 * (xedges[1] - xedges[0]), 
                              yedges[:-1] + 0.5 * (yedges[1] - yedges[0]))
            
            # 创建掩码数组，标记零值区域
            mask = h == 0
            
            # 获取原始colormap
            cmap = plt.cm.get_cmap(colormap)
            
            if colorbar_scale == '对数':
                # 清除当前图形
                self.canvas.axes.clear()
                
                # 创建自定义colormap，将零值设为黑色
                # 复制原始colormap的颜色
                colors = cmap(np.linspace(0, 1, 256))
                # 创建新的colormap，保持原始颜色
                new_cmap = ListedColormap(colors)
                
                # 对非零值进行对数变换
                h_masked = np.ma.masked_where(mask, h)
                
                # 使用LogNorm绘制非零区域
                im = self.canvas.axes.pcolormesh(
                    xedges, yedges, h_masked.T,
                    norm=LogNorm(vmin=max(1, h_masked.min())),
                    cmap=new_cmap
                )
                
                # 判断colormap的类型并设置零值区域颜色
                # 获取colormap的第一个和最后一个颜色的亮度
                first_color = colors[0]
                last_color = colors[-1]
                first_brightness = np.mean(first_color[:3])  # RGB平均值作为亮度
                last_brightness = np.mean(last_color[:3])
                
                # 根据亮度变化选择零值区域颜色
                if first_brightness > last_brightness:  # 由亮到暗
                    zero_color = 'white'
                else:  # 由暗到亮
                    zero_color = 'black'
                
                # 单独绘制零值区域
                self.canvas.axes.pcolormesh(
                    xedges, yedges, 
                    np.ma.masked_where(~mask, np.ones_like(h)).T,
                    cmap=ListedColormap([zero_color]),
                    alpha=0.9  # 调整透明度
                )
            else:
                # 线性比例，使用标准hist2d
                h, xedges, yedges, im = self.canvas.axes.hist2d(
                    x_data, y_data, 
                    bins=bins, 
                    cmap=colormap
                )
            
            # 使用简单的colorbar创建方式
            self.colorbar = self.canvas.fig.colorbar(
                im, 
                ax=self.canvas.axes,
                fraction=0.046,  # 控制colorbar宽度
                pad=0.04         # 控制colorbar与图的间距
            )
            
            # 设置colorbar标签
            scale_label = "密度 (对数比例)" if colorbar_scale == '对数' else "密度"
            self.colorbar.ax.set_ylabel(scale_label)
            
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
            
            self._configure_axes(self.canvas.axes, 
                x_major_ticks,  # 修改参数
                x_minor_ticks,  # 修改参数
                x_show_grid,    # 修改参数
                y_major_ticks,  # 添加参数
                y_minor_ticks,  # 添加参数
                y_show_grid)    # 添加参数
            # 设置坐标轴范围
            if x_min is not None and x_max is not None and x_min != x_max:
                self.canvas.axes.set_xlim(x_min, x_max)
            if y_min is not None and y_max is not None and y_min != y_max:
                self.canvas.axes.set_ylim(y_min, y_max)

            # 确保坐标轴比例自动调整
            self.canvas.axes.set_aspect('auto')
            
            # 更新画布
            self.canvas.draw()
            
            return True, "2D密度图绘制成功"
        
        except Exception as e:
            traceback.print_exc()  # 打印详细错误堆栈
            return False, f"绘制2D密度图时发生错误: {str(e)}"

    def box_plot(self, data, column, 
        title=None, 
        x_label=None, 
        y_label=None,
        color='blue',
        x_major_ticks=5,  # 修改为X轴主刻度
        x_minor_ticks=1,  # 修改为X轴次刻度
        x_show_grid=True, # 修改为X轴网格线
        y_major_ticks=5,  # 添加Y轴主刻度
        y_minor_ticks=1,  # 添加Y轴次刻度
        y_show_grid=True, # 添加Y轴网格线
        x_min=None, 
        x_max=None, 
        y_min=None, 
        y_max=None):
        
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
            
            # 设置坐标轴范围
            if x_min is not None and x_max is not None and x_min != x_max:
                self.canvas.axes.set_xlim(x_min, x_max)
            if y_min is not None and y_max is not None and y_min != y_max:
                self.canvas.axes.set_ylim(y_min, y_max)

            self._configure_axes(self.canvas.axes, 
                x_major_ticks,  # 修改参数
                x_minor_ticks,  # 修改参数
                x_show_grid,    # 修改参数
                y_major_ticks,  # 添加参数
                y_minor_ticks,  # 添加参数
                y_show_grid)    # 添加参数
            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            return True, "箱线图绘制成功"
        except Exception as e:
            return False, f"箱线图绘制失败: {str(e)}"
    
    def line_plot(self, data, x_col, y_col, 
        title=None, 
        x_label=None, 
        y_label=None, 
        color='blue', 
        alpha=0.7,
        marker='o', 
        marker_size=5, 
        linestyle='-', 
        linewidth=2,
        x_major_ticks=5,  # 修改为X轴主刻度
        x_minor_ticks=1,  # 修改为X轴次刻度
        x_show_grid=True, # 修改为X轴网格线
        y_major_ticks=5,  # 添加Y轴主刻度
        y_minor_ticks=1,  # 添加Y轴次刻度
        y_show_grid=True, # 添加Y轴网格线
        x_min=None, 
        x_max=None, 
        y_min=None, 
        y_max=None):
        
        """绘制折线图"""
        if self.canvas is None:
            return False, "画布未初始化"

        # 先清除之前的图表
        self.clear_plot()

        try:
            x = data[x_col]
            y = data[y_col]
            
            self.canvas.axes.clear()
            self.canvas.axes.plot(x, y, 
                marker=marker,
                markersize=marker_size,
                linestyle=linestyle, 
                linewidth=linewidth,
                color=color,
                alpha=alpha
            )
            
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
            
            # 设置坐标轴范围
            if x_min is not None and x_max is not None and x_min != x_max:
                self.canvas.axes.set_xlim(x_min, x_max)
            if y_min is not None and y_max is not None and y_min != y_max:
                self.canvas.axes.set_ylim(y_min, y_max)

            self._configure_axes(self.canvas.axes, 
                x_major_ticks,  # 修改参数
                x_minor_ticks,  # 修改参数
                x_show_grid,    # 修改参数
                y_major_ticks,  # 添加参数
                y_minor_ticks,  # 添加参数
                y_show_grid)    # 添加参数

            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            return True, "折线图绘制成功"
        except Exception as e:
            return False, f"折线图绘制失败: {str(e)}"

    def _configure_axes(self, axes, 
                        x_major_ticks=5, x_minor_ticks=1, x_show_grid=True,
                        y_major_ticks=5, y_minor_ticks=1, y_show_grid=True):
        """配置坐标轴刻度和网格"""
        # 设置X轴主刻度
        if x_major_ticks > 0:
            axes.xaxis.set_major_locator(ticker.MaxNLocator(x_major_ticks))
        
        # 设置X轴次刻度
        if x_minor_ticks > 0:
            axes.xaxis.set_minor_locator(ticker.AutoMinorLocator(x_minor_ticks))
        
        # 设置Y轴主刻度
        if y_major_ticks > 0:
            axes.yaxis.set_major_locator(ticker.MaxNLocator(y_major_ticks))
        
        # 设置Y轴次刻度
        if y_minor_ticks > 0:
            axes.yaxis.set_minor_locator(ticker.AutoMinorLocator(y_minor_ticks))
        
        # 设置X轴网格线
        if x_show_grid:
            axes.grid(visible=True, which='both', axis='x', linestyle='--', alpha=0.5)
        else:
            axes.grid(visible=False, axis='x')
            
        # 设置Y轴网格线
        if y_show_grid:
            axes.grid(visible=True, which='both', axis='y', linestyle='--', alpha=0.5)
        else:
            axes.grid(visible=False, axis='y')