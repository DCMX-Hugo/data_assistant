#数据分析模块
import numpy as np

class DataAnalyzer:
    def __init__(self, df):
        self.df = df
        self.analysis = {}
        self.issues = []

    def analyze_data(self):
        if self.df is None or self.df.empty:
            self.issues.append("分析失败: 数据未加载或为空")
            return

        try:
            # 1. 基本统计信息
            self.analysis['summary'] = self.df.describe(include='all').round(2).to_dict()

            # 2. 相关性分析
            numeric_cols = self.df.select_dtypes(include=np.number).columns
            if len(numeric_cols) > 1:
                self.analysis['correlation'] = self.df[numeric_cols].corr().round(2).to_dict()

            # 3. 分类变量分析
            categorical_cols = self.df.select_dtypes(exclude=[np.number, 'datetime']).columns
            categorical_report = {}

            for col in categorical_cols:
                value_counts = self.df[col].value_counts().head(10)
                categorical_report[col] = {
                    'unique_count': self.df[col].nunique(),
                    'top_values': value_counts.to_dict()
                }

            if categorical_report:
                self.analysis['categorical'] = categorical_report

            # 4. 时间序列分析 (如果有日期列)
            datetime_cols = self.df.select_dtypes(include='datetime').columns
            time_report = {}

            for col in datetime_cols:
                time_report[col] = {
                    'min_date': str(self.df[col].min()),
                    'max_date': str(self.df[col].max()),
                    'duration': str(self.df[col].max() - self.df[col].min())
                }

            if time_report:
                self.analysis['time_series'] = time_report

            print("数据分析完成")

        except Exception as e:
            self.issues.append(f"分析过程中出错: {str(e)}")
            print(f"分析错误: {str(e)}")