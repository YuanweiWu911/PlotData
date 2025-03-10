import pandas as pd
import numpy as np
import os

class DataManager:
    def __init__(self):
        self.data = None
        self.file_path = None
        self.file_name = None
    
    def load_data(self, file_path):
        """从文件加载数据"""
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        
        # 根据文件扩展名选择不同的加载方法
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.csv':
                self.data = pd.read_csv(file_path)
            elif ext == '.txt':
                # 尝试检测分隔符
                self.data = pd.read_csv(file_path, sep=None, engine='python')
            elif ext in ['.xlsx', '.xls']:
                # 添加对Excel文件的支持
                self.data = pd.read_excel(file_path)
            elif ext == '.json':
                # 添加对JSON文件的支持
                self.data = pd.read_json(file_path)
            else:
                raise ValueError(f"不支持的文件类型: {ext}")
            
            return True, "数据加载成功"
        except Exception as e:
            return False, f"数据加载失败: {str(e)}"
    
    def get_data(self):
        """获取当前数据"""
        return self.data
    
    def get_column_names(self):
        """获取列名列表"""
        if self.data is not None:
            return list(self.data.columns)
        return []
    
    def get_selected_data(self, columns, rows=None):
        """获取选定的数据"""
        if self.data is None:
            return None
        
        if rows is None:
            # 如果没有指定行，则选择所有行
            selected_data = self.data[columns]
        else:
            # 如果指定了行，则选择指定的行和列
            selected_data = self.data.iloc[rows][columns]
            
        return selected_data
    
    def get_file_info(self):
        """获取当前文件信息"""
        if self.file_name:
            return {
                'file_name': self.file_name,
                'file_path': self.file_path,
                'rows': len(self.data) if self.data is not None else 0,
                'columns': len(self.data.columns) if self.data is not None else 0
            }
        return None
    
    def preprocess_data(self):
        """预处理数据，处理缺失值和异常值"""
        if self.data is None:
            return False, "没有数据可处理"
        
        try:
            # 记录原始数据行数
            original_rows = len(self.data)
            
            # 删除全为NaN的行
            self.data.dropna(how='all', inplace=True)
            
            # 对数值列进行异常值检测（使用IQR方法）
            numeric_cols = self.data.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                Q1 = self.data[col].quantile(0.25)
                Q3 = self.data[col].quantile(0.75)
                IQR = Q3 - Q1
                
                # 定义异常值边界
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # 标记异常值
                self.data[f'{col}_outlier'] = ((self.data[col] < lower_bound) | 
                                               (self.data[col] > upper_bound))
            
            # 记录处理后的行数
            processed_rows = len(self.data)
            
            return True, f"数据预处理完成，移除了 {original_rows - processed_rows} 行空数据"
        except Exception as e:
            return False, f"数据预处理失败: {str(e)}"
    
    def get_statistics(self, column=None):
        """获取数据统计信息"""
        if self.data is None:
            return None
        
        try:
            if column:
                # 获取单列统计信息
                if column not in self.data.columns:
                    return None
                
                series = self.data[column]
                
                # 检查是否为数值列
                if pd.api.types.is_numeric_dtype(series):
                    stats = {
                        "列名": column,
                        "数据类型": str(series.dtype),
                        "非空值数": series.count(),
                        "空值数": series.isna().sum(),
                        "最小值": series.min(),
                        "最大值": series.max(),
                        "平均值": series.mean(),
                        "中位数": series.median(),
                        "标准差": series.std(),
                        "四分位数": {
                            "25%": series.quantile(0.25),
                            "50%": series.quantile(0.5),
                            "75%": series.quantile(0.75)
                        }
                    }
                else:
                    # 非数值列统计
                    stats = {
                        "列名": column,
                        "数据类型": str(series.dtype),
                        "非空值数": series.count(),
                        "空值数": series.isna().sum(),
                        "唯一值数": series.nunique(),
                        "最常见值": series.mode()[0] if not series.mode().empty else None,
                        "最常见值出现次数": series.value_counts().iloc[0] if not series.value_counts().empty else 0
                    }
                
                return stats
            else:
                # 获取整体统计信息
                numeric_data = self.data.select_dtypes(include=['number'])
                if not numeric_data.empty:
                    return numeric_data.describe().to_dict()
                else:
                    return {"error": "没有数值列可以统计"}
        except Exception as e:
            return {"error": str(e)}

    def analyze_correlation(self, columns=None):
        """分析列之间的相关性"""
        if self.data is None:
            return None, "没有数据可分析"
        
        try:
            # 如果没有指定列，则使用所有数值列
            if columns is None:
                numeric_data = self.data.select_dtypes(include=['number'])
                if numeric_data.empty:
                    return None, "没有数值列可以分析"
                corr_matrix = numeric_data.corr()
            else:
                # 检查指定的列是否都是数值类型
                for col in columns:
                    if col not in self.data.columns:
                        return None, f"列 '{col}' 不存在"
                    if not pd.api.types.is_numeric_dtype(self.data[col]):
                        return None, f"列 '{col}' 不是数值类型"
                
                corr_matrix = self.data[columns].corr()
            
            return corr_matrix, "相关性分析完成"
        except Exception as e:
            return None, f"相关性分析失败: {str(e)}"
    
    def analyze_distribution(self, column):
        """分析单列的分布情况"""
        if self.data is None:
            return None, "没有数据可分析"
        
        try:
            if column not in self.data.columns:
                return None, f"列 '{column}' 不存在"
            
            series = self.data[column]
            
            # 检查是否为数值列
            if pd.api.types.is_numeric_dtype(series):
                # 计算分布统计量
                stats = {
                    "count": series.count(),
                    "mean": series.mean(),
                    "std": series.std(),
                    "min": series.min(),
                    "25%": series.quantile(0.25),
                    "50%": series.quantile(0.5),
                    "75%": series.quantile(0.75),
                    "max": series.max(),
                    "skewness": series.skew(),  # 偏度
                    "kurtosis": series.kurtosis()  # 峰度
                }
                
                # 判断分布类型
                from scipy import stats as sp_stats
                
                # 正态性检验
                k2, p_normal = sp_stats.normaltest(series.dropna())
                
                if p_normal > 0.05:
                    distribution_type = "正态分布"
                else:
                    # 检查是否为对数正态分布
                    non_negative = series[series > 0]
                    if len(non_negative) > 0.8 * len(series):  # 如果80%以上的值为正
                        _, p_lognormal = sp_stats.normaltest(np.log(non_negative))
                        if p_lognormal > 0.05:
                            distribution_type = "对数正态分布"
                        else:
                            distribution_type = "非参数分布"
                    else:
                        distribution_type = "非参数分布"
                
                stats["distribution_type"] = distribution_type
                stats["p_normal"] = p_normal
                
                return stats, "分布分析完成"
            else:
                # 分类数据分析
                value_counts = series.value_counts()
                unique_count = series.nunique()
                
                stats = {
                    "count": series.count(),
                    "unique_values": unique_count,
                    "top_values": value_counts.head(10).to_dict(),
                    "is_categorical": unique_count < 0.1 * len(series)  # 如果唯一值少于10%，认为是分类变量
                }
                
                return stats, "分布分析完成"
        except Exception as e:
            return None, f"分布分析失败: {str(e)}"
    
    def clean_data(self, options=None):
        """清洗数据"""
        if self.data is None:
            return False, "没有数据可清洗"
        
        if options is None:
            options = {
                "drop_na": False,  # 是否删除含有空值的行
                "fill_na": False,  # 是否填充空值
                "fill_method": "mean",  # 填充方法：mean, median, mode, value
                "fill_value": 0,  # 自定义填充值
                "drop_duplicates": False,  # 是否删除重复行
                "convert_numeric": False,  # 是否尝试将字符串列转换为数值
                "round_decimals": None,  # 四舍五入小数位数
            }
        
        try:
            # 记录原始数据行数和列数
            original_rows = len(self.data)
            original_cols = len(self.data.columns)
            
            # 创建数据副本进行操作
            cleaned_data = self.data.copy()
            
            # 删除空值行
            if options.get("drop_na", False):
                cleaned_data.dropna(inplace=True)
            
            # 填充空值
            if options.get("fill_na", False):
                fill_method = options.get("fill_method", "mean")
                
                # 对数值列应用填充
                numeric_cols = cleaned_data.select_dtypes(include=['number']).columns
                
                if fill_method == "mean":
                    for col in numeric_cols:
                        cleaned_data[col].fillna(cleaned_data[col].mean(), inplace=True)
                elif fill_method == "median":
                    for col in numeric_cols:
                        cleaned_data[col].fillna(cleaned_data[col].median(), inplace=True)
                elif fill_method == "mode":
                    for col in numeric_cols:
                        mode_value = cleaned_data[col].mode()
                        if not mode_value.empty:
                            cleaned_data[col].fillna(mode_value[0], inplace=True)
                elif fill_method == "value":
                    fill_value = options.get("fill_value", 0)
                    cleaned_data.fillna(fill_value, inplace=True)
                
                # 对非数值列填充空字符串
                non_numeric_cols = cleaned_data.select_dtypes(exclude=['number']).columns
                for col in non_numeric_cols:
                    cleaned_data[col].fillna("", inplace=True)
            
            # 删除重复行
            if options.get("drop_duplicates", False):
                cleaned_data.drop_duplicates(inplace=True)
            
            # 尝试将字符串列转换为数值
            if options.get("convert_numeric", False):
                for col in cleaned_data.columns:
                    if cleaned_data[col].dtype == 'object':
                        try:
                            # 尝试转换为数值
                            cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')
                        except:
                            pass  # 如果转换失败，保持原样
            
            # 四舍五入小数
            round_decimals = options.get("round_decimals")
            if round_decimals is not None and isinstance(round_decimals, int):
                numeric_cols = cleaned_data.select_dtypes(include=['float']).columns
                for col in numeric_cols:
                    cleaned_data[col] = cleaned_data[col].round(round_decimals)
            
            # 更新数据
            self.data = cleaned_data
            
            # 计算变化
            cleaned_rows = len(self.data)
            cleaned_cols = len(self.data.columns)
            
            # 确保在所有路径上都定义了success变量
            success = True
            return success, f"数据清洗完成，处理前: {original_rows} 行，处理后: {len(cleaned_data)} 行"
        except Exception as e:
            return False, f"数据清洗失败: {str(e)}"