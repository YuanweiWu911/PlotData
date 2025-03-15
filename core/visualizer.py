def density_map_2d(self, data, x_col, y_col, bins=50, colormap='viridis'):
    """绘制2D密度图"""
    try:
        # 清除当前图表
        self.clear_figure()
        
        # 提取数据，确保转换为数值类型
        x_data = pd.to_numeric(data[x_col], errors='coerce')
        y_data = pd.to_numeric(data[y_col], errors='coerce')
        
        # 移除NaN值
        mask = ~(np.isnan(x_data) | np.isnan(y_data))
        x_data = x_data[mask]
        y_data = y_data[mask]
        
        if len(x_data) == 0 or len(y_data) == 0:
            raise ValueError("数据处理后没有有效值可用于绘图")
        
        # 使用numpy的histogram2d而不是直接使用matplotlib的hexbin
        # 这样可以更好地控制数据处理过程
        H, xedges, yedges = np.histogram2d(x_data, y_data, bins=bins)
        
        # 转置H以匹配imshow的期望格式
        H = H.T
        
        # 创建网格中心点
        x_centers = (xedges[:-1] + xedges[1:]) / 2
        y_centers = (yedges[:-1] + yedges[1:]) / 2
        
        # 使用pcolormesh绘制密度图
        X, Y = np.meshgrid(x_centers, y_centers)
        pcm = self.ax.pcolormesh(X, Y, H, cmap=colormap)
        
        # 添加colorbar
        cbar = self.fig.colorbar(pcm, ax=self.ax)
        cbar.set_label('密度')
        
        # 设置标签
        self.ax.set_xlabel(x_col)
        self.ax.set_ylabel(y_col)
        self.ax.set_title(f"{x_col} vs {y_col} 密度图")
        
        # 更新图表
        self.canvas.draw()
        print("2D密度图绘制成功")
        
    except Exception as e:
        print(f"绘制2D密度图时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise