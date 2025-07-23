#可视化模块
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from .utils import fig_to_base64, set_chinese_font

class DataVisualizer:
    def __init__(self, df):
        self.df = df
        self.visualizations = []
        self.issues = []
        set_chinese_font()  # 确保中文字体设置

    def create_visualizations(self):
        if self.df is None or self.df.empty:
            self.issues.append("可视化失败: 数据未加载或为空")
            return

        try:
            # 1. 数值变量分布
            numeric_cols = self.df.select_dtypes(include=np.number).columns
            for col in numeric_cols:
                plt.figure(figsize=(10, 6))
                sns.histplot(self.df[col], kde=True)
                plt.title(f'{col} 分布')
                plt.xlabel(col)
                plt.ylabel('频数')
                img_data = fig_to_base64(plt)
                plt.close()

                self.visualizations.append({
                    'type': 'distribution',
                    'title': f'{col} 分布',
                    'image': img_data
                })

            # 2. 分类变量计数
            categorical_cols = self.df.select_dtypes(exclude=[np.number, 'datetime']).columns
            for col in categorical_cols[:3]:  # 限制最多3个分类变量
                plt.figure(figsize=(10, 6))
                sns.countplot(y=col, data=self.df, order=self.df[col].value_counts().index[:10])
                plt.title(f'{col} 分布')
                plt.xlabel('计数')
                plt.ylabel(col)
                img_data = fig_to_base64(plt)
                plt.close()

                self.visualizations.append({
                    'type': 'categorical',
                    'title': f'{col} 分布',
                    'image': img_data
                })

            # 3. 相关性热力图
            if len(numeric_cols) > 1:
                plt.figure(figsize=(10, 8))
                corr = self.df[numeric_cols].corr()
                sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
                plt.title('变量相关性热力图')
                img_data = fig_to_base64(plt)
                plt.close()

                self.visualizations.append({
                    'type': 'correlation',
                    'title': '变量相关性',
                    'image': img_data
                })

            # 4. 数值变量关系散点图
            if len(numeric_cols) > 1:
                plt.figure(figsize=(10, 8))
                sns.pairplot(self.df[numeric_cols[:4]], diag_kind='kde')  # 限制最多4个变量
                plt.suptitle('数值变量关系', y=1.02)
                img_data = fig_to_base64(plt)
                plt.close()

                self.visualizations.append({
                    'type': 'pairplot',
                    'title': '数值变量关系',
                    'image': img_data
                })

            # 5. 时间序列分析 (如果有日期列)
            datetime_cols = self.df.select_dtypes(include='datetime').columns
            if datetime_cols.size > 0 and numeric_cols.size > 0:
                date_col = datetime_cols[0]
                numeric_col = numeric_cols[0]

                # 按时间聚合
                time_df = self.df.set_index(date_col)[numeric_col].resample('M').mean()

                plt.figure(figsize=(12, 6))
                time_df.plot()
                plt.title(f'{numeric_col} 随时间变化')
                plt.xlabel('日期')
                plt.ylabel(numeric_col)
                plt.grid(True)
                img_data = fig_to_base64(plt)
                plt.close()

                self.visualizations.append({
                    'type': 'timeseries',
                    'title': f'{numeric_col} 随时间变化',
                    'image': img_data
                })

            print(f"创建了 {len(self.visualizations)} 个可视化图表")

        except Exception as e:
            self.issues.append(f"可视化过程中出错: {str(e)}")
            print(f"可视化错误: {str(e)}")