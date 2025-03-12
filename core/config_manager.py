import os
import json
import logging

class ConfigManager:
    """配置管理器，用于保存和加载用户配置"""
    
    def __init__(self):
        self.logger = logging.getLogger("PlotData.ConfigManager")
        self.config_dir = os.path.join(os.path.expanduser("~"), ".plotdata")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # 默认配置
        self.default_config = {
            "recent_files": [],
            "max_recent_files": 10,
            "theme": "light",
            "default_plot_type": "散点图",
            "default_plot_color": "blue",
            "default_dpi": 300,
            "window_size": [800, 600],
            "window_position": [100, 100],
            "show_grid": True,
            "auto_save_settings": False,
            "decimal_places": 2
        }
        
        # 当前配置
        self.config = self.default_config.copy()
        
        # 确保配置目录存在
        self._ensure_config_dir()
        
        # 加载配置
        self.load_config()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(self.config_dir):
            try:
                os.makedirs(self.config_dir)
                self.logger.info(f"创建配置目录: {self.config_dir}")
            except Exception as e:
                self.logger.error(f"创建配置目录失败: {str(e)}")
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 更新配置，保留默认值
                    for key, value in loaded_config.items():
                        self.config[key] = value
                self.logger.info("配置文件加载成功")
            except Exception as e:
                self.logger.error(f"加载配置文件失败: {str(e)}")
        else:
            self.logger.info("配置文件不存在，使用默认配置")
            self.save_config()  # 保存默认配置
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            self.logger.info("配置已保存")
            return True
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        
        # 如果启用了自动保存，则立即保存
        if self.config.get("auto_save_settings", False):
            self.save_config()
    
    def add_recent_file(self, file_path):
        """添加最近打开的文件"""
        recent_files = self.config.get("recent_files", [])
        
        # 如果文件已在列表中，先移除
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # 添加到列表开头
        recent_files.insert(0, file_path)
        
        # 限制列表长度
        max_files = self.config.get("max_recent_files", 10)
        self.config["recent_files"] = recent_files[:max_files]
        
        # 保存配置
        if self.config.get("auto_save_settings", False):
            self.save_config()
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.config = self.default_config.copy()
        self.save_config()
        return True