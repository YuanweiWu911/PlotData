# PlotData

PlotData是一款基于Python的交互式数据可视化工具，提供简单易用的界面，帮助用户快速加载、处理和可视化数据。

## 功能特点

- **多格式数据支持**：支持CSV、Excel、JSON等多种数据格式的导入和导出
- **数据处理**：提供数据清洗、筛选、统计分析等功能
- **丰富的可视化**：支持散点图、折线图、柱状图、饼图、直方图、箱线图等多种图表类型
- **图表自定义**：可自定义标题、轴标签、颜色、样式等图表属性
- **主题切换**：支持深色/浅色主题切换
- **配置保存**：自动保存用户偏好设置和最近打开的文件

## 安装

1. 克隆仓库到本地：

```bash
git clone https://github.com/YuanweiWu911/PlotData.git

cd PlotData
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 运行程序:
```bash
python main.py
```
## 使用说明
1. 通过菜单栏或拖拽方式加载数据文件
2. 使用数据清洗功能处理缺失值和异常值
3. 在数据视图页面进行筛选和排序
4. 在统计视图页面查看数据统计信息
5. 在绘图视图页面创建和自定义图表
6. 导出处理后的数据或保存图表
## 项目结构
```plaintext
PlotData/
├── ui/                  # 用户界面模块
│   ├── main_window.py  # 主窗口
│   ├── data_view.py     # 数据视图
│   ├── stats_view.py    # 统计视图
│   └── plot_view.py     # 绘图视图
├── core/                # 核心功能模块
│   ├── data_manager.py  # 数据管理
│   └── config_manager.py # 配置管理
├── tests/               # 测试代码
└── README.md            # 项目文档
 ```

 ## 贡献指南
 欢迎提交 Issue 和 Pull Request。请确保：

 1. 代码符合 PEP8 规范
 2. 添加必要的单元测试
 3. 更新相关文档
 ## 许可证
 MIT License

 ```plaintext

 这个 README 更新包含了：
 1. 项目概述和主要功能
 2. 系统要求和安装指南
 3. 使用说明
 4. 项目结构
 5. 贡献指南
 6. 许可证信息

 所有信息都基于当前工程代码中的实际功能，特别是从 `data_manager.py`、`main_window.py` 等核心文件中提取的功能描述。
  ```
